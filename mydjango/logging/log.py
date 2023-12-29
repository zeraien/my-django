import datetime
from traceback import format_exc

from django.conf import settings
from django.utils import timezone

LEVELS = ['JOB', 'DEBUG', 'INFO', 'WARN', 'ERROR']

def debug(msg,request = None):
    log('DEBUG',msg, request)

def warn(msg,request = None):
    log('WARN',msg, request)

def exception_warn(msg = None, request = None):
    error(msg=msg, exception_str=format_exc(), request=request,level="WARN")
def exception_debug(msg = None, request = None):
    error(msg=msg, exception_str=format_exc(), request=request,level="DEBUG")
def exception(msg, request=None):
    error(msg,exception_str=format_exc(),request=request)
    
def error(msg, exception_str=None, request = None, level = "ERROR"):
    title = msg
    if exception_str is not None:
        msg = msg is not None and msg or u''
        msg += u"\n"
        msg += exception_str
    log(level=level, msg=msg, request=request)
    from django.core.mail import mail_admins

    if level in ('ERROR','WARN'):
        mail_admins(subject=u"[%s] Error message logged: %s" % (level, title),
            message=msg,
            fail_silently=True
        )
    
def info(msg,request = None):
    log('INFO', msg, request)

def log(level, msg, request = None):
    from mydjango.logging.models import LogEntry
    localtime = timezone.now()
    ctime = localtime.ctime()
    fancytime = localtime.strftime("%Y-%m-%d %H:%M")
    try:
        if request is not None:
            ip = request.META.get('REMOTE_ADDR','Unknown IP')
        else:
            ip = None
        if settings.DEBUG:
            print(u"""[%(level)s] %(fancytime)s: %(msg)s""" % locals())
        LogEntry.objects.create(level=level, message=msg, ip_address=ip, created_at=localtime)
    except Exception, e:
        if not settings.DEBUG:
            print level, localtime.ctime(), msg
        print u"Additional errors occured when trying to save log message to database: %s", e
        print format_exc()
