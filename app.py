import os
import imghdr

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, abort
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import datetime

from helpers import apology, login_required


# Configure application
app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif', '.jpeg', '.JPG', '.PNG']
app.config['UPLOAD_PATH'] = 'static/images'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show all posts"""

    database = db.execute("SELECT id, users.username, profile.picture, posts.posts, posts.date FROM users JOIN profile ON users.id = profile.user_id JOIN posts ON users.id = posts.user_id ORDER BY date DESC")

    return render_template("index.html", database=database)



@app.route("/index_profile_link/<int:id>", methods=["GET", "POST"])
@login_required
def index_profile_link(id):
    """Click a username in index to go to their profile"""

    if request.method == "GET":

        user_id = session["user_id"]

        # Accounts for selecting own username
        if user_id == id:
            return redirect("/view_profile")

        # Variables
        i = db.execute("SELECT picture FROM profile WHERE user_id=?", id)
        picture = i[0]["picture"]

        database = db.execute("SELECT name, email, bio FROM profile WHERE user_id=?", id)
        username = db.execute("SELECT username FROM users WHERE id=?", id)
        posts = db.execute("SELECT post_id, posts, date FROM posts WHERE user_id=? ORDER BY date DESC", id)
        search_username = username[0]["username"]

        # Check if user and selected username entered are friends
        j = db.execute("SELECT friend_id FROM friends WHERE user_id = ? AND friend_username = ?", user_id, search_username)


        if len(j):
            # Show friend's profile with selected username's id
            return render_template("view_friend_profile.html", database=database, username=username, picture=picture, id=id, posts=posts)

        else:
            # Show other users profile with selected username's id
            return render_template("view_other_profile.html", database=database, username=username, picture=picture, id=id, posts=posts)

    else:
        pass



@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    """Post a status"""
    if request.method == "GET":

        # Show all user's posts

        user_id = session["user_id"]

        every_user_id = db.execute("SELECT id from users")

        for i in every_user_id:

            if i["id"] == user_id:

                j = db.execute("SELECT picture FROM profile WHERE user_id=?", user_id)
                picture = j[0]["picture"]

                k = db.execute("SELECT username FROM users WHERE id=?", user_id)
                username = k[0]["username"]

                database = db.execute("SELECT post_id, posts, date FROM posts WHERE user_id=? ORDER BY date DESC", user_id)

                return render_template("post.html", database=database, picture=picture, username=username, id=user_id)

    else:
        # User adds a post
        post = request.form.get("post")

        if not post:
            return apology("Must provide a post!")

        user_id = session["user_id"]

        date = datetime.datetime.now()

        db.execute("INSERT INTO posts (user_id, posts, date) VALUES (?, ?, ?)", user_id, post, date)

        flash("Posted!")

        return redirect("/post")



@app.route("/delete_post/<int:id>", methods=["GET", "POST"])
@login_required
def delete_post(id):
    """Allows users to delete posts"""

    if request.method == "GET":

        return redirect("/post")

    else:

        db.execute("DELETE FROM posts WHERE post_id=?", id)

        flash("Deleted!")

        return redirect("/post")


@app.route("/view_profile", methods=["GET", "POST"])
@login_required
def profile():
    """Allows user to view their profile"""

    if request.method == "GET":

        user_id = session["user_id"]

        i = db.execute("SELECT picture FROM profile WHERE user_id=?", user_id)

        picture = i[0]["picture"]

        database = db.execute("SELECT name, email, bio FROM profile WHERE user_id=?", user_id)
        username= db.execute("SELECT username FROM users WHERE id=?", user_id)

        return render_template("view_profile.html", database=database, username=username, picture=picture)

    else:
        pass


# Function to validate profile picture uploads
def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Allows user to edit their profile"""

    if request.method == "GET":

        # Checking database for bio to display in edit profile
        user_id = session["user_id"]
        bio_database = db.execute("SELECT bio FROM profile WHERE user_id=?", user_id)
        bio = bio_database[0]["bio"]

        if bio != '':
            return render_template("edit_profile.html", bio=bio)

        else:
            # No previous bio, show placeholder
            return render_template("edit_profile.html")

    else:
        # Allows user to update picture, name, email and bio
        user_id = session["user_id"]

        # If a file is uploaded for a profile picture, assign it a variable and add to static folder
        uploaded_file = request.files["picture"]
        filename = secure_filename(uploaded_file.filename)

        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']: #or file_ext != validate_image(uploaded_file.stream):

                return apology("Photo file is not valid", 400)

            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

            # Assign variable for filename to keep consistent with other variables
            picture = filename


        else:
            # If no file uploaded, pull picture that is already in the database
            i = db.execute("SELECT picture FROM profile WHERE user_id=?", user_id)

            picture = i[0]["picture"]


        name = request.form.get("name")
        email = request.form.get("email")
        bio = request.form.get("bio")

        #update profile info
        db.execute("UPDATE profile SET picture=?, name=?, email=?, bio=? WHERE user_id=?", picture, name, email, bio, user_id)

        flash("Updated!")

        return redirect("/view_profile")



@app.route("/friend_list", methods=["GET", "POST"])
@login_required
def friend_list():
    """View the users friend list"""
    if request.method == "GET":

        user_id = session["user_id"]

        # Create a list of the user's friends

        username_database = db.execute("SELECT friend_username FROM friends WHERE user_id=?", user_id)

        friends = []

        for i in range(len(username_database)):
            friends.append(username_database[i]['friend_username'])

        # Create a list of the users friend's ids

        select_id_database = db.execute("SELECT id FROM users WHERE username IN (?)", friends)

        ids = []

        for i in range(len(select_id_database)):
            ids.append(select_id_database[i]['id'])

        # Create a variable for the users friends info
        friends_database = db.execute("SELECT picture, id, username FROM users JOIN profile ON id = user_id WHERE id IN (?)", ids)

        # Update ids to include the user
        ids.append(user_id)

        #Create a variable for other users info
        other_database = db.execute("SELECT picture, id, username FROM profile JOIN users ON id = user_id WHERE id NOT IN (?)", ids)

        return render_template("friend_list.html", friends_database=friends_database, other_database=other_database)

    else:
        pass


@app.route("/search_profile", methods=["GET", "POST"])
@login_required
def search_friend():
    """Search for another users profile"""

    if request.method == "GET":

        pass

    else:
        # Variables
        search_username = request.form.get("search")
        user_id = session["user_id"]
        i = db.execute("SELECT id FROM users WHERE username = ?", search_username)

        # Check a username has been entered
        if not search_username:
            return apology("Must provide a username!")

        # Check username exists
        elif len(i) != 1:
            return apology("Username does not exist!")

        # Searched username's id
        id = i[0]["id"]

        # Check if user searched for themselves
        if id == user_id:
            return redirect("/view_profile")

        # Searched username's profile info
        j = db.execute("SELECT picture FROM profile WHERE user_id=?", id)
        picture = j[0]["picture"]

        database = db.execute("SELECT name, email, bio FROM profile WHERE user_id=?", id)
        username = db.execute("SELECT username FROM users WHERE id=?", id)
        posts = db.execute("SELECT post_id, posts, date FROM posts WHERE user_id=? ORDER BY date DESC", id)

        # Check if user and searched username entered are friends
        k = db.execute("SELECT friend_id FROM friends WHERE user_id = ? AND friend_username = ?", user_id, search_username)

        if len(k):
            # Show friend's profile with searched username's id
            return render_template("view_friend_profile.html", database=database, username=username, picture=picture, id=id, posts=posts)

        else:
            # Show other users profile with searched username's id
            return render_template("view_other_profile.html", database=database, username=username, picture=picture, id=id, posts=posts)



@app.route("/view_other_profile/<int:id>", methods=["GET", "POST"])
@login_required
def view_other_profile(id):
    """View another users profile with the ability to add as a friend"""

    if request.method == "GET":
        # View a users profile

        i = db.execute("SELECT picture FROM profile WHERE user_id=?", id)

        picture = i[0]["picture"]

        database = db.execute("SELECT name, email, bio FROM profile WHERE user_id=?", id)
        username= db.execute("SELECT username FROM users WHERE id=?", id)
        posts = db.execute("SELECT post_id, posts, date FROM posts WHERE user_id=? ORDER BY date DESC", id)

        return render_template("view_other_profile.html", database=database, username=username, picture=picture, id=id, posts=posts)

    else:
        # Add them as a friend

        i = db.execute("SELECT username FROM users WHERE id=?", id)

        username = i[0]["username"]

        user_id = session["user_id"]

        db.execute("INSERT INTO friends (user_id, friend_username) VALUES (?, ?)", user_id, username)

        flash("Friend Added!")

        return redirect("/friend_list")



@app.route("/view_friend_profile/<int:id>", methods=["GET", "POST"])
@login_required
def view_friend_profile(id):
    """View a friends profile with the ability to remove as a friend"""

    if request.method == "GET":
        # View a friends profile

        i = db.execute("SELECT picture FROM profile WHERE user_id=?", id)

        picture = i[0]["picture"]

        database = db.execute("SELECT name, email, bio FROM profile WHERE user_id=?", id)
        username= db.execute("SELECT username FROM users WHERE id=?", id)
        posts = db.execute("SELECT post_id, posts, date FROM posts WHERE user_id=? ORDER BY date DESC", id)

        return render_template("view_friend_profile.html", database=database, username=username, picture=picture, id=id, posts=posts)

    else:
        # Remove them as a friend

        i = db.execute("SELECT username FROM users WHERE id=?", id)

        username = i[0]["username"]

        user_id = session["user_id"]

        db.execute("DELETE FROM friends WHERE user_id = ? AND friend_username = ?", user_id, username)

        flash("Friend Removed!")

        return redirect("/friend_list")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("Must give username!")

        elif not password:
            return apology("Must give password!")

        elif not confirmation:
            return apology("Must give confirmation of password!")

        elif password != confirmation:
            return apology("Password and Confirmation must match!")

        hash = generate_password_hash(password)

        try:
            # Inserting username and hash of password into our database
            new_user = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)

        except:
            return apology("Username already exists!")

        session["user_id"] = new_user

        # Create the user a blank profile in our database

        user_id = session["user_id"]

        db.execute("INSERT INTO profile (user_id, picture, name, email, bio) VALUES (?, ?, ?, ?, ?)", user_id, '', '', '', '')

        return redirect("/")


@app.route("/delete_account", methods=["GET", "POST"])
@login_required
def delete_account():
    """Allows user to delete their account"""
    if request.method == "GET":
        return render_template("delete_account.html",)

    else:

        user_id = session["user_id"]

        # Check password/confirmation have been entered and that they match
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not password:
            return apology("Must give password!")

        elif not confirmation:
            return apology("Must give confirmation of password!")

        elif password != confirmation:
            return apology("Password and Confirmation must match!")

        # Check that password matches hash in database

        rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("Invalid password", 403)

        # SQL queries to delete users info from database
        db.execute("DELETE FROM posts WHERE user_id=?", user_id)
        db.execute("DELETE FROM profile WHERE user_id=?", user_id)
        db.execute("DELETE FROM friends WHERE user_id=?", user_id)
        db.execute("DELETE FROM users WHERE id=?", user_id)

        # Clear the session and redirect to login/register page

        session.clear()

        return redirect("/")
