# pyspace
#### Video Demo:  https://www.youtube.com/watch?v=yimB9ycjL6E
#### Description:
The basis of my project was to create a social media platform akin to something like Facebook or Myspace. Having used social media for the past 15 years of my life without really understanding the fundamentals of how one works behind the scenes, I thought creating one for my final project for CS50 would provide me with some insight.

The **frontend** is comprised of HTML, CSS and the bootstrap framework whereas the backend uses a SQL database, python and the flask framework. Thus the name pyspace is a combination of the prefix py (associated with the python code) and space (derived from myspace).

Firstly, the HTML, CSS and bootstrap I tried to keep to a more minimalist style as I think this helps the webapp look cleaner and more sophisticated. The colour scheme is also more of a dark theme with complementary light and dark blues.

In my **SQL database** there are 4 main tables; users, posts, profile and friends.

Users has a primary id which all other tables derive a foreign id, as well as a username and password hash that was created on registration.
Posts keeps track of each post a user makes as well as the datetime of the post.
Profile allows a user to save a profile picture, name, email address and a bio.
Friends keeps account of the relationship between a user id and the username of the friend they wish to add.

Before I cover each route in app.py I think its important to point out the constants of the webapp, those being layout.html and helpers.py

**layout.html** is the master html template that all others are derived from. Here we set up the ability to use bootstrap and our css code as well as aesthetic bits like icons and flashed messages. The most important part however, this is where the nav bar is set up that allows us to navigate our webapp.

**helpers.py** is a small file that provides two key functions, a function called apology that helps with error and exception handling and a login_required function that we use to decorate routes in app.py when a login is required to access that code, if the login function is not satisfied then it is defaulted to the login html page which asks for a users username and password.

#### app.py and HTML templates

Firstly in app.py we must import the necessary libraries, configure the flask app and SQL database and finally there is a function to ensure responses aren't cached.

**index** is our main route. This is the news feed and pulls all the needed information from our database such as; the post itself, the username and profile picture of the user that created the post and the datetime which is how the posts are ordered (from newest to oldest) and displayed. I have considered many more features for this part of the app such as allowing users to be able to upload pictures or videos as well as incorporating like/dislike/comment functionality to the posts. However, due to the time constraints of the course I decided to keep it more streamlined but may be something I come back to at a later date.

#### post and delete_post

Speaking of posts, it makes sense to discuss the **post** and **delete_post** routes together. By selecting posts on the navbar the post route uses the GET method to display the post.html page. This page displays a textbox where a post can be written and submitted via the POST method of our post route, this then inserts a SQL query in our database and creates a post_id. This post will be updated to index but also all the of the users previous posts (including the new one) can be seen in a table in posts, each has a delete button next to them. When clicked this takes the post_id and uses the POST method of the delete_post route to remove the entry from our database.

#### profile and edit_profile

Two other routes worth discussing together are **profile** and **edit_profile**. When profile is selected on the navbar, the view_profile route is run which runs the code under the GET method for profile. This is fairly simple as it pulls the profile picture, name, email and bio from our profile table and the username from users table and renders the view_profile template.

All users are provided with a blank profile as part of the registration route when making an account, by default this is blank and a default profile picture. However, there is an edit button on view_profile that redirects to the edit_profile html page via the GET method. Here the user can upload a new profile picture, name, email address and bio then press update which runs the POST method of edit_profile. The name, email and bio are all simply uploaded to our database to be recalled at a later date but we need to do some extra checks for the photograph.

At the top of our code we have assigned the max content length to be 1mb, upload extentions to be limited to those of known picture types and defined the upload path of any uploads to be our static/images folder. We also have a validate_image function that opens and reads the first 512 bytes of the file to confirm if this is an image file or not. In our edit_profile code we can then use these tools to check our photo, first we request the file and set a variable for the secure filename. Then we split the filename and check if the file type is consistient with our upload extentions and to see if the image can pass the validate_image function, if not the error/apology function is run. If both checks are passed we save the image to our upload path (static/images) and set the filename a variable so that we can save the filename in our database to call on at a later date. (It is important to note that the image itself is not being sorted in our SQL database, only the filename. The image is being held in static/images so later in our code when we try to reference the photo we use the path static/images/{{ 'filename' }}).

I have currently commented out the validate_image check as a lot of images were deemed invalid. For the most part this is just to make it more convienient for me to create new profiles without having to worry about the pictures too much. However, if it were to be hosted on a public server I would advise "turning it on" to counter someone with malevolent intentions.

#### friends list

friends_list.html is only accessable by the GET method and has 3 main parts, a search bar to search for a user, a list of the users friends and a list of all other users that are not friends. To understand how this piece of code works we need to understand how the friend info is stored in our database. When a friend is added (more on how to do that later) a new row in the friend table is created, with a friend_id, the user_id that added the friend and the username of the friend. In order to display this info in our friends list there needs to be a bit of unpacking. First we have to pull all the usernames of friends associated with the current users id, we then store them in a list. With that list we then find all the user id's that correspond with the usernames in our list from the user table and store those ids in a seperate list.
With this list of friends ids we can pull all the information needed from our database to display a list of the users friends (pictures, username, id for viewing profile etc). We can then also pull all the other information from the database of users that are NOT friends with this user and display them in a seperate list for other users. There is a unqiue case that the users info would be shown in this other list which is why we add their id to the list to account for this. (The user doesn't need to see their profile info in the list of other users).

#### view_other_profile and view_friend_profile

These two routes and HTML files are very similar but also work in opposition to each other. On our friends list there is a button to view each users profile, both routes take a user id as an input and then display that users profile via the GET method. The key difference though is that on a friends profile there is a button to remove them as a friend, clicking this uses the POST method of view_friends_profile and removes that friendship from the database. Conversely on other users profiles there is a button to add them as a friend, clicking it uses the POST method of view_other_profile and adds them as a friend in the database. Both buttons then redirect you back to your friends list.

#### search_profile and index_profile_link

I intentionally left these till the end as I think they are best described together due to their similarities. Both allow for a user to view profiles of themselves, friends or other users without directly clicking on a profile button. The search profile makes use of the search bar at the top of the friends list to take in a full username (no partial username or suggestion function is available) and display that profile. The index profile link on the other hand is a hyperlink on someones name and profile picture on each post that will directly take you to their profile by the id that is provided.
The only difference in the code is the input taken (username or id) the rest is almost the same. With the input we find all the relevant information for that persons profile. We check to see if the user has chosen their own profile and redirect them to their profile via view_profile. Otherwise we check to see if they are friends with the user, if they are friends we render the view_friend_profile and if not we render the view_other_profile.

My biggest regret for this project comes from this part of the code as there is a lot of redundency and repetition of code. The ideal scenario I was trying to achieve was to use redirect in flask. After getting the id of the user from search_profile and index_profile_link and checking for self-search/friends/other users I wanted to redirect to view_other_profile or view_friend_profile respectively by passing the id in the url. However, after reading the documentation for flask, searching on Google, Youtube and Stackoverflow I wasn't able to find a suitable answer so had to settle for pulling the information from the database and rendering the relevant template. This element of redundancy would only get more pronounced the more features were added which is why it's what I would like to change about the code the most.

I would hope login, logout, register and delete account would be fairly self-explanatory but in the interest of being thorough I'll cover them briefly here.

**Register** supports both the GET and POST methods. When GET is used it renders the register HTML template, which is a form that requests a username, password and password confirmation. Clicking the register button submits the form to the POST method where all the form information is requested. There are then a series of checks to check a username has been entered and isn't already in use, a password and confirmation have been entered and they match. If the checks are passed a hash is created for the password for security purposes, we then create the users session id and generate the user's blank profile before redirecting to index.

**login** clears the session before displaying a form for logging in. A username and password must be entered before clicking the log in submit button via the POST method. Checks are again done to confirm a username and password has been entered, then to check the username exists and the password matches the hash password check. If these are passed then the session id is updated to the user_id, hence logging in and redirecting to index. The GET method just returns the user to the login screen.

**log out** is the simplist route that just clears the users session and redirects them to the login page.

Finally, **delete_account** via the GET method can be accessed from the navbar. This renders the delete_account HTML page, which is a page that warns the user that once an account has been deleted it can't be recovered or undone. The user can fill the form in by entering their password and confirming it. Similar checks are made to ensure something is entered, the password and confirmation match and matches the password hash in the database. If these checks are passed then the users id is deleted from each table in our database before being redirected to the login screen. Another feature could be to have a history to restore deleted users but for the time being I didn't think this necessary.