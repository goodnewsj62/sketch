from sqlalchemy.sql.expression import desc

from . import db


# Handels database calls used by the app 
class Database:
    def __init__(self,User,Post,Notification,follow):
        self.user = User
        self.post = Post
        self.notification = Notification
        self.follow = follow


    def get_all_post(self):
        return self.post.query.all()
    
    def get_notified_post(self,user):
        return self.post.query.join(self.follow, (self.follow.c.followed_id == self.post.uploader)).filter(self.follow.c.follower_id == user.id).order_by(self.post.date_posted.desc()).all()
    
    def get_user(self,user_id):
        return self.user.query.get(user_id)
    
    def get_user_by_username(self,username):
        return self.user.query.filter_by(username=username).first()

    def get_user_by_email(self,email):
        return self.user.query.filter_by(email=email).first()
    
    def get_user_by_social_id(self,social_id):
        return self.user.query.filter_by(social_id=social_id).first()
    
    def check_username(self,username):
        if self.user.query.filter_by(username=username).first():
            return True
        return False

    def validate_user(self,bcrypt_,username,password):
        user = self.get_user_by_username(username)
        if user and  bcrypt_.check_password_hash(user.password,password):
            return user
        else:
            return None

    def validate_password(self,password):
        if password == None:
            raise Exception('no password input')
        
        errors = []
        passed = True

        if len(password) < 7:
            errors.append('password must be up to 7 characters long')
            passed = False
        if not any(n.isupper() for n in password):
            errors.append('password must contain capital letter')
            passed = False

        if not any(n.isdigit() for n in password):
            errors.append('password must contain a number')
            passed = False

        return passed, errors
        
    
    def create_user(self, name, username, email,contact, password):
        if contact == None or len(contact) == 0:
            user = self.user(name=name, username=username, email=email,password=password)
            db.session.add(user)
            db.session.commit()
            return True
        elif not contact == None and len(contact) > 4:
            user = self.user(name=name, username=username, email=email,contact =contact,password=password)
            db.session.add(user)
            db.session.commit()
            return True
        else:
            return False



    def follow(self,user,to_follow):
        if not self.get_user(user.id).is_following(to_follow):
            self.get_user(user.id).notified.append(to_follow)
            db.session.commit()
            return True


    def unfollow(self, user,to_unfollow):
        if self.get_user(user.id).is_following(to_unfollow):
            self.get_user(user.id).notified.remove(to_unfollow)
            db.session.commit()
            return True
