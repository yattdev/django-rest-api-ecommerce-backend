# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from aptusadmin.forms import ConnexionForm, Change_password
from aptusadmin.models import CustomUser
from aptusadmin.templatetags.aptusadmin_filter import get_dirname
from aptusadmin.settings import CONNECTION_URL


def connexion(request):
    error_message = ''
    if request.method == "POST":
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"].lower()
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)  # Nous vérifions si les données sont correctes
            if user and user.is_active:
                login(request, user) 
                if user.must_change_pwd is True and 'primary_user' not in request.session:
                    return redirect(reverse('aptusadmin:change_password'))
                next = request.GET['next'] if 'next' in request.GET else ''
                return redirect(CONNECTION_URL + f"?next={next}")
            else: # sinon une erreur sera affichée
                error_message = 'Utilisateur inconnu ou mauvais mot de passe.'
    else:
        form = ConnexionForm()
    return render(request, 'aptusadmin/connexion.html', {'form':form, 'error_message':error_message})

def deconnexion(request):
    logout(request)
    return redirect(reverse('aptusadmin:connexion'))

import requests

def set_screen_size(request):
    size = request.GET.get('size')
    if size:
        request.session['screen_size'] = size
    return HttpResponse(status=200)

@login_required
def change_password(request):
    custom_user = request.user
    if request.method == 'POST':
        form = Change_password(request.POST)
        if form.is_valid():
            if( request.POST['action'] == 'Enregistrer'):
                if custom_user.check_password(form.cleaned_data["old_password"]):
                    if form.cleaned_data['new_password'] == form.cleaned_data['confirmation_password']:
                        if form.cleaned_data['old_password'] != form.cleaned_data['new_password']:
                            custom_user.set_password(request.POST['new_password'])
                            if custom_user.must_change_pwd == True:
                                custom_user.must_change_pwd = False
                                custom_user.tmp_pwd = ''
                            custom_user.save()
                            new_auth = authenticate(username=custom_user.username, password=request.POST['new_password'])
                            login(request, new_auth)
                            messages.add_message(request, messages.INFO, "Votre mot de passe a été modifié.", extra_tags='alert-success')
                            #return HttpResponseRedirect(get_dirname(request.path))
                            return redirect(CONNECTION_URL)
                        else:
                            messages.add_message(request, messages.INFO,
                            "Le nouveau mot de passe doit être différent de l'ancien.", extra_tags='alert-danger')
                            return HttpResponseRedirect(request.path)
                    else :
                        messages.add_message(request, messages.INFO, "Les deux mots de passe ne correspondent pas.", extra_tags='alert-danger')
                        return HttpResponseRedirect(request.path)
                else :
                    messages.add_message(request, messages.INFO, "Votre ancien mot de passe est incorrect. Veuillez le rectifier.", extra_tags='alert-danger')
                    return HttpResponseRedirect(request.path)
    else:
        form = Change_password()
    return render(request, 'aptusadmin/change_password.html', {'form':form})

def activate(request, uid, token):
    protocol = 'https://' if request.is_secure() else 'http://'
    web_url = protocol + request.get_host()
    post_url = web_url + "/auth/users/activation/"
    post_data = {'uid': uid, 'token': token}
    requests.post(post_url, data = post_data)
    messages.add_message(request, messages.INFO, "Votre compte a été vérifiez, vous pouvez maintenant vous y connecter", extra_tags="alert-info")
    return(redirect("/"))

from aptusadmin.forms import PasswordResetForm

def password_reset(request, uid, token):
    form = PasswordResetForm(form_type='pwd_form')
    step = 2
    context = {
        'pwd_form': form,
        'step': step,
        'uid': uid,
        'token': token
    }
    return render(request, "aptusadmin/email_validation/password_reset_form2.html", context)

def password_reset_confirm(request):
    form = PasswordResetForm(form_type='pwd_form')
    step = 3
    context = {
        'connection_url': "/",
        'pwd_form': form,
        'step': step
    }
    return render(request, "aptusadmin/email_validation/password_reset_form2.html", context)

def signup(request):
    return render(request, 'aptusadmin/signup.html')