# -*- coding: utf-8 -*-
from datetime import datetime

from myapps.models import CustomUser, Alert
from myapps.settings import SCREEN_WIDTH_MIN
from myapps.templatetags.myapps_filter import localize

try:
    from aptusparc.local_settings import message_alert
    msg_alert = message_alert
except ImportError:
    msg_alert = ''

def mycontext(request):
    user = request.user if request.user.is_authenticated() else None

    show_apis_menu = user.has_perm('aptusadmin.viewlist_api') if user else False
    if show_apis_menu:
        try:
            import google_auth_oauthlib
        except ImportError:
            show_apis_menu = False

    return {
        'user_messages': CustomUser.objects.get(user_ptr=user).get_massages() if user else None,
        'user_alerts': CustomUser.objects.get(user_ptr=user).get_alerts() if user else None,
        'current_appli':request.path.split("/")[1],
        'get_alerts': Alert.c_list(),
        'now': localize(datetime.utcnow()),
        'MOBILE_REDIRECT': 'http://aptus.ma',
        'SCREEN_WIDTH_MIN': SCREEN_WIDTH_MIN,
        'show_apis_menu': show_apis_menu,
    }
