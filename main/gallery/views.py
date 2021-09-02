from functools import wraps, update_wrapper
import os
import uuid
import base64

from flask import Blueprint,abort,session,redirect,request,render_template
from flask_login import login_required,current_user

from main.database import Database
from main.models import Post,User,Notification,follow

gallery = Blueprint("gallery",__name__)




@gallery.route('/', methods=['GET'])
@gallery.route('/home',methods=['GET'])
def home():
    return  render_template('gallery/home.html')

    
# @gallery.route('/gallery', method=['GET'])
# def gallery():
#     pass

# @gallery.route("/details", methods=['GET'])
# def details():
#     pass

# @gallery.route("/search", methods=['GET'])
# def search():
#     pass

# @gallery.route("/posts/<username>", methods=["GET"])
# def users_posts(username):
#     pass

# @gallery.route("/notifications",methods=["GET"])
# @login_required
# def notifications():
#     pass

# @gallery.route("/dashboard",methods=["GET"])
# @login_required
# def dashboard():
#     pass

# @gallery.route("/upload", methods=["GET","POST"])
# @login_required
# def upload():
#     pass

# @gallery.route("/upload/<id>", methods=["GET"])
# def get_uploaded(id):
#     pass

# @gallery.route("/user/profile/<id>", methods=["GET"])
# def user_profile(id):
#     pass

# @gallery.route("/user/profile",methods=["GET","POST"])
# @login_required
# def profile():
#     pass

# @gallery.route("/update/<id>",methods=["GET","POST"])
# @login_required
# def update_post(id):
#     pass

# @gallery.route("/delete/<id>", methods = ["GET","POST"])
# @login_required
# def delete_post(id):
#     pass

# @gallery.route("/follow/<id>", methods=["GET","POST"])
# @login_required
# def follow(id):
#     pass

# @gallery.route("/unfollow/<id>", methods=["GET","POST"])
# @login_required
# def unfollow(id):
#     pass

# @gallery.route("/following", methods=["GET"])
# @login_required
# def following():
#     pass