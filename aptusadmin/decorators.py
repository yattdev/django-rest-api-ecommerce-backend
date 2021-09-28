# -*- coding: utf-8 -*-

from django.shortcuts import redirect, render
from django.urls import reverse


def valid_session(view):
    def wrap(request, *args, **kwargs):
        if request.user.has_perm('aptusadmin.access_to_admin_console') and (
                request.user.must_change_pwd == False or 'primary_user' in request.session):
            return view(request, *args, **kwargs)
        else:
            return redirect(reverse('aptusadmin:deconnexion'))
    return wrap
