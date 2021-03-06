import json

from rauth import OAuth1Service, OAuth2Service
from flask import current_app, url_for, request, redirect, session




class OAuthSignIn(object):
    """
        - OAuthSignIn is like a blue print other class would subclass and overide methods, making use 
        of init data. 
        - the authorize method is used to send the user to thirdparty site to authenticate
        - the callback method does filter_checks and return a useful response for login of specific user
        - the third party site cant access methods but can access an endpoint/url which the get_callback_url
        gets and its used to call the callback method
        - the classmethod uses the provider_name to get the right class to be called and initialized
    """
    providers = None

    #gets needed credentials
    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('auth.oauth_callback', provider=self.provider_name,_external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class FacebookSignIn(OAuthSignIn):
    """
        - This class subclass OAuthSignIn and overides some of its methods 
        - calls init of parent class and uses data eg: self.consumer_id
        - initiliaze OAuth2Service and stores it to service
    """
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service =OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://www.facebook.com/dialog/oauth',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                    'grant_type': 'authorization_code',
                    'redirect_uri': self.get_callback_url()},
            decoder=decode_json
        )
        me = oauth_session.get('me?fields=id,email').json()
        return 'facebook$' + me['id'],me.get('email').split('@')[0],me.get('email') 
        # Facebook does not provide
        # username, so the email's user
        # is used instead


class TwitterSignIn(OAuthSignIn):
    def __init__(self):
        super(TwitterSignIn, self).__init__('twitter')
        self.service = OAuth1Service(
            name='twitter',
            consumer_key=self.consumer_id,
            consumer_secret=self.consumer_secret,
            request_token_url='https://api.twitter.com/oauth/request_token',
            authorize_url='https://api.twitter.com/oauth/authorize',
            access_token_url='https://api.twitter.com/oauth/access_token',
            base_url='https://api.twitter.com/1.1/'
        )

    def authorize(self):
        request_token = self.service.get_request_token(
            params=json.dumps({'oauth_callback': self.get_callback_url()})
        )
        session['request_token'] = request_token
        return redirect(self.service.get_authorize_url(request_token[0]))

    def callback(self):
        request_token = session.pop('request_token')
        if 'oauth_verifier' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            request_token[0],
            request_token[1],
            data={'oauth_verifier': request.args['oauth_verifier']}
        )
        me = oauth_session.get('account/verify_credentials.json').json()
        social_id = 'twitter$' + str(me.get('id'))
        username = me.get('screen_name')
        return social_id, username, None   # Twitter does not provide email


class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        self.service =OAuth2Service(
            name='google',
            client_id = self.consumer_id,
            client_secret= self.consumer_secret,
            base_url= "https://www.googleapis.com/oauth2/v3/",
            access_token_url='https://www.googleapis.com/oauth2/v3/token',
            authorize_url='https://accounts.google.com/o/oauth2/v2/auth'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(scope = 'openid email profile',response_type="code",redirect_uri=self.get_callback_url()))
        
    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))
            _

        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                    'grant_type': 'authorization_code',
                    'redirect_uri': self.get_callback_url()},
            decoder=decode_json
        )

        me = oauth_session.get("userinfo").json()
        return 'google$' + me['sub'],me.get('given_name'),me.get('email') 