import json
import os
import uuid
import base64

from flask import Blueprint,flash,render_template,url_for,redirect
from flask_login import login_required,current_user

from .. import db as maindb
from .form import UpdateProfile,AvatarForm
from ..database import Database
from ..models import User,Post,Notification,follow

user = Blueprint("user", __name__)

db = Database(User,Post,Notification,follow)

@user.route("/profile", methods=["GET","POST"])
@login_required
def profile():
    form = UpdateProfile()
    user = db.get_user_by_username(current_user.username)

    facebook = None
    twitter = None
    linkedin = None
    instagram = None

    payload = json.loads(str(user.accounts))
    if 'facebook' in payload:
        facebook = payload['facebook']
    if 'twitter' in payload:
        twitter = payload['twitter']
    if 'instagram' in payload:
        instagram = payload['instagram']
    if 'linkedin' in payload:
        linkedin = payload['linkedin']
    
    

    if form.validate_on_submit():
        payload = {"facebook":form.facebook.data, "instagram":form.instagram.data, "twitter":form.twitter.data\
            ,"linkedin":form.linkedin.data}
        payload = json.dumps(payload)

        user.name = form.name.data
        user.username = form.username.data
        user.email = form.email.data
        user.contact = form.contact.data
        user.bio = form.bio.data
        user.accounts = payload
        maindb.session.commit()

        flash("profile update successful","success")
        return redirect(url_for("user.profile"))
    

    form.name.data = user.name
    form.username.data = user.username
    form.email.data = user.email
    form.contact.data = user.contact
    form.bio.data = user.bio
    form.facebook.data = facebook
    form.twitter.data = twitter
    form.instagram.data = instagram
    form.linkedin.data = linkedin
    
    return render_template("user/profile",form=form)

@user.route("/profile/avatar",methods=["GET","POST"])
@login_required
def change_avatar():
    form = AvatarForm()
    user = db.get_user_by_username(current_user.username)

    if form.validate_on_submit():
        pass

def avatar():
    pass

