from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User

from aptusadmin.models import CustomUser
from aptusadmin.settings import CONNECTION_URL


@login_required
def send_validation_link(request):

    user = request.user
    customuser = CustomUser.objects.get(user_ptr=user)
    if user.email and customuser.email_is_valid is False:
        current_site = get_current_site(request)
        res, message = customuser.send_mail_activation_link(current_site.domain)
        messages.add_message(request, messages.INFO, message[1], extra_tags='alert-' + message[0])
    return redirect(CONNECTION_URL)


def activate_mail_adress(request, uidb64, mailb64, token, tcdb64):  # tcd: token creation date
    mail = ''
    token_creation_date = ''
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        token_creation_date = force_text(urlsafe_base64_decode(tcdb64))
        mail = force_text(urlsafe_base64_decode(mailb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user:
        customuser = CustomUser.objects.get(user_ptr=user.id)
        res, message = customuser.activate_mail_adress(token=token, mail=mail, token_creation_date=token_creation_date)
        messages.add_message(request, messages.INFO, message[1], extra_tags='alert-' + message[0])
        if res is True:
            login(request, user)
    return redirect(CONNECTION_URL)
