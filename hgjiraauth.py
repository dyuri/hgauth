from jira.client import JIRA
import hgauth


class HgJiraAuthMiddleware(object):
    """
    JIRA authentication for Mercurial WSGI app
    """
    def __init__(self, wsgi_app, jiraurl):
        self.jiraurl = jiraurl
        self.wsgi_app = hgauth.HgAuthMiddleware(
            wsgi_app=wsgi_app,
            authfn=self.jiraauthfn
        )

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def jiraauthfn(self, user, password, realm, environ=None):
        print 'u, p, r: %s, %s, %s' % (user, '*'*len(password), realm)
        try:
            j = JIRA(options = { 'server': self.jiraurl}, basic_auth=(user, password))
            print 'login succeeded'
            if realm and realm != 'Hg Root':
                p = j.project(realm)
                print 'project found'
        except:
            print 'authentication failed'
            return False

        return True
