# hgauth

import base64

def parse_auth_header(value):
    up = base64.b64decode(value.split()[1]).split(':')
    return {
            'user': up[0],
            'password': up[1]
            }

class HgAuthMiddleware(object):
    """
    HTTP Basic authentication middleware for mercurial

    `wsgi_app`
       The WSGI app to be secured.
    `authfn`
       The the external authorization function which is called on every request
       in the following form:
       `authfn(username, password, realm, environ)`
       - where realm is the first part of the url path (mercurial repository)
    """
    def __init__(self, wsgi_app, authfn):
        self.wsgi_app = wsgi_app
        self.authfn = authfn

    def __call__(self, environ, start_response):
        if not self.authenticate(environ):
            # user hasn't sent authentication/wrong credentials.
            return self.challenge(environ, start_response)
        else:
            # Wave-through to real WSGI app.
            return self.wsgi_app(environ, start_response)

    def get_realm(self, environ):
         path = environ['PATH_INFO'].split('/')
         return path[1] if len(path) > 1 and path[1] != '' else 'Hg Root'

    def authenticate(self, environ):
        """
        Returns True if the credentials passed in the Authorization header are
        valid, False otherwise.
        """
        try:
            hd = parse_auth_header(environ['HTTP_AUTHORIZATION'])
        except:
            return False

        return self.authfn(hd['user'], hd['password'], self.get_realm(environ), environ)

    def challenge(self, environ, start_response):
        start_response(
            '401 Authentication Required',
            [('WWW-Authenticate', 'Basic realm="%s"' % self.get_realm(environ))],
        )
        return ['<h1>401 - Authentication Required</h1>']

