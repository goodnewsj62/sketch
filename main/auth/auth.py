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
from .. import db as maindb
from ..oauth import OAuthSignIn
from ..database import Database
from .form import LoginForm,RegisterForm,ChangePassword
from main.models import User,Post,Notification,follow,Role


providers = ['twitter','google','facebook']

auth = Blueprint('auth',__name__,url_prefix='/auth')

#from database class to handle all db queries
db = Database(User,Post,Notification,follow)

@login_manager.user_loader
def load_user(user_id):
    return db.get_user(user_id)

#function blocks user logged in from accessing
#the login page again
def annonymous(view):
    @wraps(view)
    def wrapper(*arg,**kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("gallery.home"))
        return view(*arg,**kwargs)
    return update_wrapper(wrapper, view)


@auth.route('/login', methods=['GET','POST'])
@annonymous
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user = db.validate_user(bcrypt_,form.username.data, form.password.data)

        if user != None:
            login_user(user,form.remember.data)
            flash('sign in successful', 'success')
            return redirect(url_for('gallery.home'))
        else:
            error = "invalid password"

    return render_template('auth/signin.html', err = error, form=form)
        


@auth.route('/register', methods=['GET','POST'])
@annonymous
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if db.get_user_by_username(form.username.data):
            flash('username already exist', 'danger')
            return redirect(url_for('auth.login'))
        if db.get_user_by_email(form.email.data):
            flash('Email already exist', 'danger')
            return redirect(url_for('auth,login'))

        passed,errors = db.validate_password(form.password.data)

        if passed:
            password = bcrypt_.generate_password_hash(form.password.data).decode('utf-8')
            if db.create_user(name = form.name.data,username= form.username.data,email=form.email.data,
                                        contact=form.contact.data,password=password):
                flash('Account created successfully', 'success')
                return redirect(url_for('gallery.home'))
        
        else:
            return render_template('auth/signup.html', err=errors, form= form)


    return render_template('auth/signup.html', form= form)


@auth.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash('you have successfully signed out', 'success')
    return redirect(url_for('gallery.home'))


@auth.route('/forgot/pasword/<username>')
def request_password(username):
    user = db.get_user_by_username(username)
    base_url = request.url_root
    response = ""

    if user:

        payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        "iat": datetime.datetime.utcnow(),
        "user_id": user.id
        }

        if user.email and len(user.email) > 6:
            token = jwt.encode(payload,current_app.secret_key,algorithm="HS256")
            url = base_url + f"/auth/reset/password/token/{token}/{username}"
            message = f"""
                    <p>Ignore if you did not expect this</p>
                    <p>
                        You have requested for a new password
                        To reset your password click the link below
                    </p>
                    <a href="{url}">{url}</a>
                    
                    <p>Thank you.</p>
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

    return render_template("auth/password_message.html", response = response)

            


@auth.route("/reset/password/token/<token>/<username>")
def password_change(token,username):
    try:
        payload = jwt.decode(token,current_app.secret_key,algorithms="HS256")
        user_id = payload["user_id"]
        

        errors = None
        if user_id:
            user = db.get_user(user_id)
            if request.method == "POST":
                password = request.form["password"]
                passed,errors = db.validate_password(password)
                if passed:
                    user.password = bcrypt_.generate_password_hash(password).decode('utf-8')
                    maindb.session.commit()
                    flash("Password reser successful","success")
                    return render_template("auth/password.html")
            
        return render_template("auth/password.html", err=errors)
    except jwt.ExpiredSignatureError:
        flash("This link has expired click on forget password again","danger")
        return redirect(url_for("auth.register"))
    except jwt.InvalidTokenError or jwt.InvalidSignatureError:
        flash("Invalid link", "danger")

    return render_template("auth/password.html")


@auth.route("/change/password",methods =["GET","POST"])
@login_required
def password_reset():
    form = ChangePassword()

    if form.validate_on_submit():
        user = db.get_user_by_username(current_user.username)
        passed,errors= db.validate_password(form.password.data)

        if passed:
            user.password = bcrypt_.generate_password_hash(form.password.data).decode("utf-8")
            maindb.session.commit()
            flash("password reset successful", "success")
            return redirect(url_for("gallery.home"))
        else:
            return render_template("auth/resetpassword.html", err=errors, form=form)

    return render_template("auth/resetpassword.html", form=form)


@auth.route('/validusername/<username>')
def valid_username(username):
    if db.get_user_by_username(username):
        return True
    return False


@auth.route('/authorize/<provider>')
@annonymous
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
@annonymous
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
    user = db.get_user_by_social_id(social_id)
    
    username_pass = db.check_username(username)

    while (username_pass == True):
        username =  username + str(randint(1,6000000))
        username_pass = db.check_username(username)

    if not user:
        if email == None:
            email == ''
        
        # random password is used since password cant be a null field
        # and we cant use either email,social_id or username to create password
        # this prevent someone from signing in knowing the username email and id
        user = User(social_id=social_id, name=username_ ,username=username, email=email,password=bcrypt_.generate_password_hash(secrets.token_hex(16)).decode('utf-8'))
        maindb.session.add(user)
        maindb.session.commit()
    login_user(user, True)
    flash('sign in successful', 'success')
    return redirect(url_for('gallery.home'))




