from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User

from aptusadmin.settings import CONNECTION_URL
from aptusadmin.forms import PasswordResetForm
from aptusadmin.models import CustomUser


def send_password_reset_link(request):

    if request.method == 'GET':
        form = PasswordResetForm(form_type='email_form')
    else:
        form = PasswordResetForm(request.POST, form_type='email_form')
        if form.is_valid():

            customuser = CustomUser.objects.filter(email=form.cleaned_data['email'], email_is_valid=True).first()

            current_site = get_current_site(request).domain
            res, message = customuser.send_password_reset_mail(current_site)
            messages.add_message(request, messages.INFO, message[1], extra_tags='alert-' + message[0])


    context = {
        'connection_url': CONNECTION_URL,
        'email_form': form,
        'step': 1,
    }
    return render(request, 'aptusadmin/email_validation/password_reset_form.html', context)


def reset_password(request, uidb64, token, tcdb64):  # tcd: token creation date
    reverse_url = ''
    token_creation_date = ''
    back_url = 'aptusadmin:connection'
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        token_creation_date = force_text(urlsafe_base64_decode(tcdb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user:
        customuser = CustomUser.objects.get(user_ptr=user.id)
        step = 2
        if request.method == 'GET':
            form = PasswordResetForm(form_type='pwd_form')
            customuser.token_valid = True
            res, message = customuser.check_token_validity(token=token, token_creation_date=token_creation_date)

            if not res:
                messages.add_message(request, messages.INFO, message[1], extra_tags='alert-' + message[0])

        else:
            form = PasswordResetForm(request.POST, form_type='pwd_form')
            if form.is_valid():
                res, message = customuser.check_token_validity(token=token, token_creation_date=token_creation_date)

                if res:
                    customuser.reset_password(form.cleaned_data['new_password'], permanent=True)
                    step = 3
                else:
                    messages.add_message(request, messages.INFO, message[1], extra_tags='alert-' + message[0])

        context = {
            'pwd_form': form,
            'step': step,
        }
        return render(request, 'aptusadmin/email_validation/password_reset_form.html', context)
    return redirect(reverse('aptusadmin:connexion'))
