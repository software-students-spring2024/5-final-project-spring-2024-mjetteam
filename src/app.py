#!/usr/bin/env python3

import os
import datetime
from flask import Flask, render_template, request, redirect, url_for

# from markupsafe import escape
import pymongo
from dotenv import load_dotenv
import flask_login #this will be used for user authentication
from flask_bcrypt import Bcrypt 
from flask_login import LoginManager
from bson.decimal128 import Decimal128
from bson.objectid import ObjectId #used to search db using objec ids
# load credentials and configuration options from .env file
# if you do not yet have a file named .env, make one based on the template in env.example
load_dotenv()  # take environment variables from .env.

# instantiate the app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

bcrypt = Bcrypt(app) 
#these 2 are for flask login
login_manager = LoginManager()
login_manager.init_app(app)

#if using Atlas database uncomment next line!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! and comment out the next four lines
client = pymongo.MongoClient(os.getenv("MONGO_URI"))

#if using containerized instance of mongo uncomment next 4 lines else comment them out
#root_username = os.environ["MONGO_INITDB_ROOT_USERNAME"]  #1
#root_password = os.environ["MONGO_INITDB_ROOT_PASSWORD"]  #2
#uri = f"mongodb://{root_username}:{root_password}@mongodb:27017/db?authSource=admin" #3
#client = pymongo.MongoClient(uri) #4

db = client[os.getenv("MONGO_DBNAME")]  # store a reference to the database

# the following try/except block is a way to verify that the database connection is alive (or not)
try:
    # verify the connection works by pinging the database
    client.admin.command("ping")  # The ping command is cheap and does not require auth.
    print(" *", "Connected to MongoDB!")  # if we get here, the connection worked!
except Exception as e:
    # the ping command failed, so the connection is not available.
    print(" * MongoDB connection error:", e)  # debug

# set up the routes


# # turn on debugging if in development mode
# if os.getenv("FLASK_ENV", "development") == "development":
#     # turn on debugging, if in development
#     app.debug = True  # debug mnode
    

#this is the class user which will be stored in a session
#i think the flask_login.Usermixin handles all of the methods needed
class User(flask_login.UserMixin):
    pass


#this callback is used to reload the user object from the user ID stored in the session.It should take the str ID of a user, and return the corresponding user object
@login_manager.user_loader
def user_loader(username):
    founduser = db.users.find_one({"username": username})
    if not founduser: 
        return

    user = User()
    user.id = founduser["_id"]
    return user


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    founduser = db.users.find_one({"username": username})
    if not founduser: 
        return

    user = User()
    user.id = username
    return user


@app.route("/")
def home():
    """
    Route for the home page
    """
    sort_option = request.args.get('sort')

    if sort_option == 'oldest':
        docs_cursor = db.items.find({}).sort("created_at", 1)
    elif sort_option == 'lowest':
        docs_cursor = db.items.find({}).sort("price", 1)
    elif sort_option == 'highest':
        docs_cursor = db.items.find({}).sort("price", -1)
    else:
        docs_cursor = db.items.find({}).sort("created_at", -1)
    
    docs = list(docs_cursor)
    return render_template("index.html", docs=docs)  # render the hone template


# route to accept the form submission to delete an existing post
@app.route("/signup", methods=["POST", "GET"])
def sign_up():
    """
    Route for GET AND POST for signup page
    """
    if request.method == "POST":
        username = request.form["fusername"]
        password = request.form["fpassword"]
        user = db.users.find_one({"username": username})
        if user:
            return render_template("signup.html", error="Username already in use.")
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8') 
            new_user = {'username': username, 'password': hashed_password, 'items': []}
            db.users.insert_one(new_user)
            return redirect(url_for("log_in"))
    if flask_login.current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template("signup.html")


@app.route("/login", methods=["POST", "GET"])
def log_in():
    """
    Route for GET AND POST for login page
    """
    if request.method == "POST":
        username = request.form["fusername"]
        password = request.form["fpassword"]
        found_user = db.users.find_one({"username": username})
        if not found_user:
            return render_template('login.html', error="User not found.")
        else:
            is_valid = bcrypt.check_password_hash(found_user['password'], password)
            if not is_valid:
                return render_template('login.html', error="Username or password is invalid.") 
            user = User()
            user.id = username
            flask_login.login_user(user)
            return redirect(url_for('home'))
    if flask_login.current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template("login.html")


@app.route('/protected')
@flask_login.login_required
def protected():
    return render_template('protected.html') 


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('log_in'))

@app.route("/item/<item_id>")
@flask_login.login_required
def item(item_id):
    try:
        founditem = db.items.find_one({'_id': ObjectId(item_id)})
        return render_template("item.html", founditem = founditem)
    except:
        return redirect(url_for('home')) #redirect to an error page ideally

#add item here
@app.route("/add")
@flask_login.login_required
def add():
    #TODO make this an actual userid fetch
    try:
        userid = flask_login.current_user.id
        return render_template("add.html", userid = userid)
    except:
        #error handle
        return redirect(url_for('home'))

@app.route("/add/<user_id>", methods= ["GET", "POST"])
@flask_login.login_required
def create_item(user_id):
    user = db.users.find_one({"_id":ObjectId(user_id)})
    print(user)
    username = user["username"]
    name = request.form["itemname"]
    desc = request.form["description"]
    price = Decimal128(request.form["price"])
    url = request.form["url"]
    item = {"name": name,  "description" :desc, "user":ObjectId(user_id),"username":username, "image_url":url, "price": price, "created_at": datetime.datetime.utcnow()}
    db.items.insert_one(item)
    return redirect(url_for('view_listings'))

#delete has no html but should be invoked later from the my listings page, pass the item id through
@app.route("/delete/<item_id>")
@flask_login.login_required
def delete(item_id):
        db.items.delete_one({"_id": ObjectId(item_id)})
        #TODO can redirect to the my listings page later
        return redirect(url_for('view_listings'))

@app.route("/edit/<item_id>")
@flask_login.login_required
def edit(item_id):
    founditem = db.items.find_one({'_id': ObjectId(item_id)})
    return render_template("edit.html", founditem = founditem, item_id = item_id)

@app.route("/update/<item_id>", methods= ["GET", "POST"])
@flask_login.login_required
def update_item(item_id):
    name = request.form["itemname"]
    desc = request.form["description"]
    price = Decimal128(request.form["price"])
    url = request.form["url"]
    item = {"name": name,  "description" :desc, "image_url":url, "price": price}
    db.items.update_one({"_id": ObjectId(item_id)}, {"$set": item})
    return redirect(url_for('view_listings'))


@app.route("/viewListings")
@flask_login.login_required
def view_listings():
    user_to_find = flask_login.current_user.id
    print(user_to_find)
    items = list(db.items.find({"user": ObjectId(user_to_find)}))
    return render_template("viewlistings.html", docs = items)


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('log_in'))


# run the app
if __name__ == "__main__":
    # use the PORT environment variable, or default to 5000
    FLASK_PORT = os.getenv("FLASK_PORT", "5001")

    # import logging
    # logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
    app.run(host="0.0.0.0", port=FLASK_PORT)