from random import randint
import secrets
import datetime
from functools import wraps, update_wrapper
import os

from flask import Blueprint,abort,session,redirect,request,current_app,abort,flash,url_for,render_template
from flask_login import logout_user,login_user,login_required,current_user
from flask_mail import Message
import jwt

from .. import login_manager,create_app,bcrypt_,mail
from .. import db
from ..oauth import OAuthSignIn
from .form import LoginForm,RegisterForm,ChangePassword
from main.models import User,Post,Notification,follow


providers = ['twitter','google','facebook']

auth = Blueprint('auth',__name__,url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

#function blocks user logged in from accessing
#the login page again

def only_annonymous(view):
    @wraps(view)
    def wrapper(*arg,**kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("gallery.home"))
        return view(*arg,**kwargs)
    return update_wrapper(wrapper, view)


@auth.route('/login', methods=['GET','POST'])
@only_annonymous
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user =  User.query.filter_by(username=form.username.data).first()
        user = User.query.filter_by(email = form.username.data).first() if user == None else user #if user is none query by email else just assign user to user
        if user != None:
            if bcrypt_.check_password_hash(user.password,form.password.data):
                login_user(user,form.remember.data)
                next= request.values.get("next")
                flash('sign in successful', 'success')
                if next:
                    return redirect(next)
                return redirect(url_for('gallery.home'))
            else:
                flash('invalid Password')
                return redirect(url_for('auth.login'))
        else:
            flash('Invalid Username and Password')

    return render_template('auth/signin.html', form=form)
        


@auth.route('/register', methods=['GET','POST'])
@only_annonymous
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        password = bcrypt_.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name= form.name.data, username=form.username.data, email=form.email.data,password=password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        next= request.values.get("next")
        flash('Account created successfully', 'success')
        if next:
            return redirect(next)
        return redirect(url_for('gallery.home'))    

    return render_template('auth/signup.html', form= form)



@auth.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash('you have successfully signed out', 'success')
    return redirect(url_for('gallery.home'))


@auth.route('/forgot/pasword/<username>')
def request_password(username):
    user = User.query.filter_by(username=username).first()
    base_url = request.url_root
    response = ""

    if user:
        #payload contains useful information which jwt will encrypt in the link to be sent
        #exp == expiration date, iat == sent time
        payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        "iat": datetime.datetime.utcnow(),
        "user_id": user.id
        }

        if user.email and len(user.email) > 6:
            token = jwt.encode(payload,current_app.secret_key,algorithm="HS256")
            url = base_url + f"/auth/reset/password/token/{token}/{username}"

            message = f"""
                    <h2 style="background-color:#1e90ff; height:70px; width:250px; text-align:center; line-height:50%;">Sketch Password Reset <h2>
                    <p style="padding:10px 0; line-height:1.5;">Simply ignore if you dont expect this email</p>
                    <div style="padding:1rem; background-color:#ddd; line-height:1.5;">
                        <p>
                            You have requested for a new password
                            To reset your password click the link below
                        </p>
                        <a style="text-decoration:none;" href="{url}">{url}</a>
                    <h3 style="color:1e90ff;">Thank you.</h3>
                """

            msg = Message("Sketch: Password Reset",html= message,
            sender=os.environ.get("Email"),recipients=[user.email])
            try:
                mail.send(msg)

                flash("A link has been sent to email","success")
                response = "A link to reset your password has been sent to your email right away incase\
                    not seen check in email spam folder"
            except Exception as e:
                flash("An error occured try again","danger")
                response = "An error occured please try again, make sure your account has\
                    a valid email or contact help center"
                redirect(url_for("auth.register"))
        else:
            flash("This user does not have a valid email","danger")
            response = "No set valid email for this account"
    else:
        flash("no such user exist","danger")
        response ="No such user exist with the username provided"

    return render_template("auth/forgot_password.html", response = response)

            


@auth.route("/reset/password/token/<token>/<username>")
def password_change(token,username):
    try:
        #jwt decode token from url
        payload = jwt.decode(token,current_app.secret_key,algorithms="HS256")
        user_id = payload["user_id"]
        

        errors = None
        #if payload contains user_id
        if user_id:
            user = User.query.filter_by(id=user_id).first()
            if request.method == "POST":
                password = request.form["password"]
                if len(password) > 7:
                    user.password = bcrypt_.generate_password_hash(password).decode('utf-8')
                    db.session.commit()
                    flash("Password reset successful","success")
                    return render_template("auth/password.html")
        
        return render_template("auth/password.html", err=errors)
    
    except jwt.ExpiredSignatureError:
        flash("This link has expired click on forget password again","danger")
        return redirect(url_for("auth.login"))
    except jwt.InvalidTokenError or jwt.InvalidSignatureError:
        flash("Invalid link", "danger")

    return render_template("auth/password.html")


@auth.route("/change/password",methods =["GET","POST"])
@login_required
def password_reset():
    form = ChangePassword()

    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        passed= bcrypt_.check_password_hash(user.password,form.password.data)

        if passed:
            user.password = bcrypt_.generate_password_hash(form.password.data).decode("utf-8")
            db.session.commit()
            flash("password reset successful", "success")
            return redirect(url_for("gallery.home"))

    return render_template("auth/resetpassword.html", form=form)


@auth.route('/validusername/<username>')
def valid_username(username):
    if User.query.filter_by(username = username).first():
        return True
    return False


@auth.route('/authorize/<provider>')
@only_annonymous
def oauth_authorize(provider):
    """
        - if user is authenticated refer back to home
        - else call the class method that initializes class for provider
        - calls authorize to autheticate from thrid party
    """
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@auth.route('/callback/<provider>')
@only_annonymous
def oauth_callback(provider):
    """
        - if user is authenticated refer back to home
        - else call the class method that initializes class for provider
        - calls callback to handle response from thrid party
        - checks if authentication was sucessful using social_id
        - assigns unique username
    """
    if not current_user.is_anonymous:
        return redirect(url_for('gallery.home'))

    if provider  not in providers:
        abort(404)


    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()

    username_ = username
    user = User.query.filter_by(social_id=social_id).first()
    
    username_pass = True if User.query.filter_by(username).first() else False

    #if user exist in data base add a random number to username 
    # then check again if such user exist. repeat if user exist
    while (username_pass == True):
        username =  username + str(randint(1,6000000))
        username_pass = True if User.query.filter_by(username).first() else False

    if not user:
        #if no user with such social id exists
        if email == None:
            email == ''
        
        # random password is used since password cant be a null field
        # and we cant use either email,social_id or username to create password
        # this prevent someone from signing in knowing the username email and id
        user = User(social_id=social_id, name=username_ ,username=username, email=email,password=bcrypt_.generate_password_hash(secrets.token_hex(16)).decode('utf-8'))
        db.session.add(user)
        db.session.commit()
        
    login_user(user, True)
    flash('sign in successful', 'success')
    return redirect(url_for('gallery.home'))




