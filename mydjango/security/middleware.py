import datetime
from django.conf import settings
from django.contrib.auth import logout, SESSION_KEY, BACKEND_SESSION_KEY
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

LOGIN_TIMEOUT_SESSION_KEY = "_login_timeout_last_visit"

class LoginTimeoutMiddleware(object):
    """Middleware that logs the user out after a number of hours of inactivity. Default is 72.
    Use the `LOGIN_TIMEOUT_HOURS` setting in your django settings to specify a different timeout."""
    def process_request(self, request):
        assert hasattr(request, 'user'), "The MyDjango security middleware requires auth middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.auth.middleware.AuthenticationMiddleware'."

        if request.user.is_authenticated():
            if LOGIN_TIMEOUT_SESSION_KEY in request.session:
                last_visit = request.session[LOGIN_TIMEOUT_SESSION_KEY]
            else:
                last_visit = None
            request.session[LOGIN_TIMEOUT_SESSION_KEY] = timezone.now()

            timeout = getattr(settings, 'LOGIN_TIMEOUT_HOURS', 72)
            delta = datetime.timedelta(hours=timeout)

            if last_visit is None:
                last_visit = request.user.last_login
            
            try:
                diff = (timezone.now() - last_visit)
                if diff > delta:
                    # logout(request)
                    del(request.session[SESSION_KEY])
                    del(request.session[BACKEND_SESSION_KEY])
                    request.user = AnonymousUser()
            except TypeError:
                pass
            
        request.session[LOGIN_TIMEOUT_SESSION_KEY] = timezone.now()
