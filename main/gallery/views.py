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

    
@gallery.route('/library', methods=['GET'])
def library():
    return render_template('gallery/library.html')

@gallery.route("/details/<id>", methods=['GET'])
def details(id):
    post = Post.query.filter_by(id=id).first()
    # date to string function
    return render_template('gallery/details.html', post= post)

@gallery.route("/search", methods=['GET'])
def search():
    query = request.values("search") 
    if query:
        pass
    else:
        pass
    # return render_template()

@gallery.route("/posts/<username>", methods=["GET"])
def users_posts(username):
    user = User.query.filter_by(username= username).first()
    post = user.posts
    # return render_template()

@gallery.route("/notifications",methods=["GET"])
@login_required
def notifications():
    pass
    # return render_template()

@gallery.route("/dashboard",methods=["GET"])
@login_required
def dashboard():
    pass
    # return render_template()

@gallery.route("/upload", methods=["GET","POST"])
@login_required
def upload():
    pass
    # return render_template()
@gallery.route("/upload/<id>", methods=["GET"])
def get_uploaded(id):
    pass
    # return render_template()

@gallery.route("/user/profile/<id>", methods=["GET"])
def user_profile(id):
    pass
    # return render_template()

@gallery.route("/user/profile",methods=["GET","POST"])
@login_required
def profile():
    pass
    # return render_template()

@gallery.route("/update/<id>",methods=["GET","POST"])
@login_required
def update_post(id):
    pass
    # return render_template()

@gallery.route("/delete/<id>", methods = ["GET","POST"])
@login_required
def delete_post(id):
    pass
    # return render_template()

@gallery.route("/follow/<id>", methods=["GET","POST"])
@login_required
def follow(id):
    pass
    # return render_template()

@gallery.route("/unfollow/<id>", methods=["GET","POST"])
@login_required
def unfollow(id):
    pass
    # return render_template()

@gallery.route("/following", methods=["GET"])
@login_required
def following():
    pass
    # return render_template()