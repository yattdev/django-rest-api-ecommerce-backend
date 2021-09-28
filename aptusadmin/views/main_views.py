# -*- coding: utf-8 -*-
import json

from threading import Thread

from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login,logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required,permission_required
from django.shortcuts import redirect
from django.urls import reverse
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.http import JsonResponse
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from aptusadmin.forms import UtilisateurFilterForm, UtilisateurForm, GroupeFilterForm, GroupeForm, LogEntryFilterForm
from aptusadmin.models import Backup, CustomUser, CustomGroup, CustomPermission, Message, CustomLogEntry, Alert
from aptusadmin.permissions import *
from aptusadmin.templatetags.aptusadmin_filter import get_dirname, add_name, get_basename, get_dirname
from aptusadmin.settings import (
    rows_per_page, INSTALLED_APTUS_APPS, list_path_template, view_path_template, form_path_template,
    SYSTEM_PROFILES, NOM_SOLUTION, CONNECTION_URL
)
from aptusadmin.decorators import valid_session


number_by_page = rows_per_page


@login_required
def myappslist(request):
    user = request.user
    context = {
        'can_access_educat': user.has_perm('educat.access_to_appli_fi') or user.has_perm('educat.access_to_appli_fc'),
        'can_access_espace_enseignant': 'espaceenseignant' in INSTALLED_APTUS_APPS and hasattr(user, 'enseignant'),
        'can_access_enseignant': 'enseignant' in INSTALLED_APTUS_APPS and hasattr(user, 'enseignant'),
        'can_access_espace_etudiant': 'espaceetudiant' in INSTALLED_APTUS_APPS and hasattr(user, 'etudiant'),
        'can_access_myapps': user.has_perm('aptusadmin.access_to_admin_console'),
        'can_access_parc': 'parc' in INSTALLED_APTUS_APPS,
        'can_access_immo': 'immo' in INSTALLED_APTUS_APPS,
        'can_access_immoha': 'immoha' in INSTALLED_APTUS_APPS,
    }
    return render(request, 'aptusadmin/home.html', context)



@login_required
@valid_session
def admin_home (request):
    return render(request, 'aptusadmin/admin-home.html', {
        'active_accueil': True,
        'mon_solution': NOM_SOLUTION
    })

@login_required
@valid_session
def backup_restore(request):
    if not request.user.has_perm('aptusadmin.viewlist_backup'):
        raise PermissionDenied
    
    queryset = Backup.objects.all()
    paginator = Paginator(queryset,number_by_page)
    if request.GET.get('page'):
        page = request.GET.get('page')
    else:
        page=1  
    try:
        queryset_per_page = paginator.page(page)
    except PageNotAnInteger:
        queryset_per_page = paginator.page(1)
    except EmptyPage:
        queryset_per_page = paginator.page(paginator.num_pages)
    if request.method == 'POST':
        if( request.POST['action'] == 'import_backup'):
            obj = Backup()
            message = obj.c_import(request.FILES['file'])
            messages.add_message(request, messages.INFO, message[1], extra_tags='alert-'+message[0])
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if( request.POST['action'] == 'restore_backup'):
            obj =Backup.objects.get(pk=request.POST.get('id_backup'))
            message=obj.restore(pin=123456)
            messages.add_message(request, messages.INFO, message[1], extra_tags='alert-'+message[0])
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if( request.POST['action'] == 'delete_backup'):
                obj =Backup.objects.get(pk=request.POST.get('id_backup'))
                obj.c_delete()
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if( request.POST['action'] == 'create_backup'):
            if request.user.is_authenticated():
                obj = Backup()
                message = obj.c_create(user=request.user)
                messages.add_message(request, messages.INFO, message[1], extra_tags='alert-'+message[0])
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                logout(request)
                return redirect(reverse('aptusadmin:connexion'))
    context = {
        'total':queryset.count(),
        'queryset':queryset_per_page,
        'last_elt_in_page':((int(page)-1)*number_by_page)+len(queryset_per_page),
        'first_elt_in_page':((int(page)-1)*number_by_page)+1,
        'instance':Backup(),
        'enable_filter':True,
        'display_btn_plus':True,
        'active_backup':True,
        'parent_template':list_path_template
    }
              
    return render(request, 'aptusadmin/backup_restore.html', context)


@login_required
@valid_session
def utilisateurs(request):
    if not viewlist_customuser(request.user):
        raise PermissionDenied
    
    queryset, btn_filter_list = CustomUser.c_list(request.GET, request.get_full_path())
    paginator = Paginator(queryset, number_by_page)
    if request.GET.get('page'):
        page = request.GET.get('page')
    else:
        page = 1
    try:
        queryset_per_page = paginator.page(page)
    except PageNotAnInteger:
        queryset_per_page = paginator.page(1)
    except EmptyPage:
        queryset_per_page = paginator.page(paginator.num_pages)
    if request.method == 'POST':
        if( request.POST['action'] == 'Supprimer'):
            for elt in request.POST.getlist('Choix[]'):
                objet =CustomUser.objects.get(pk=elt)
                objet.c_delete()
            return HttpResponseRedirect(request.get_full_path()) 
    filterform = UtilisateurFilterForm(initial=request.GET)
    display_btn_plus = delete_customuser(request.user) 
    context = {
        'total':queryset.count(),
        'queryset':queryset_per_page,
        'last_elt_in_page':((int(page)-1)*number_by_page)+len(queryset_per_page),
        'first_elt_in_page':((int(page)-1)*number_by_page)+1,
        'btn_filter_list':btn_filter_list,
        'instance':CustomUser(),
        'can_add':add_customuser(request.user),
        'can_delete':delete_customuser(request.user),
        'enable_filter':True,
        'display_btn_plus':display_btn_plus,
        'filterform':filterform,
        'active_utilisateurs':True,
        'parent_template':list_path_template
    }
    return render(request, 'aptusadmin/utilisateur/utilisateur-liste.html', context)


@login_required
@valid_session
def utilisateur_consulter(request, **kwargs):     
    if not view_customuser(request.user):
        raise PermissionDenied
    instance = CustomUser.objects.get(pk=kwargs['utilisateur_id'])
    prev, next, num_instance, total_instance=CustomUser.myapps_manager.get_prev_and_next_items(instance, CustomUser.c_list(request.GET, request.get_full_path())[0])
    if request.method == 'POST':
        if request.POST['action'] == 'Reinitialiser_password':
            instance.pwd_gen()
            messages.add_message(request, messages.INFO, "Mot de passe réinitialisé avec succès.",
                                 extra_tags='alert-success')
            return HttpResponseRedirect(request.get_full_path())
        if request.POST['action'] == 'Supprimer':
            instance.c_delete()
            messages.add_message(request, messages.INFO, 'Suppression effectuée avec succès', extra_tags='alert-success')
            return HttpResponseRedirect(get_dirname(request.get_full_path()))

        elif request.POST['action'] == 'take_identity':
            primary_user_id = request.user.id
            current_user = CustomUser.objects.get(id=request.user.id)

            target_user = get_user_model().objects.get(id=instance.id)
            current_user.switch_account(request, target_user)

            request.session['primary_user'] = primary_user_id

            return redirect(CONNECTION_URL)

    display_btn_plus = True if delete_customgroup(request.user) else False
    context = {
        'instance':instance,
        'prev':prev,
        'next': next , 
        'num_instance': num_instance, 
        'total_instance': total_instance,
        'can_add':add_customuser(request.user),
        'can_delete':delete_customuser(request.user),
        'can_change':change_customuser(request.user),
        'can_take_identity': can_take_identity(request.user),
        'active_utilisateurs':True,
        'display_btn_plus':display_btn_plus,
        'parent_template':view_path_template
    }    
    return render(request, 'aptusadmin/utilisateur/utilisateur-consulter.html', context)


@login_required
@valid_session
def utilisateur_creer(request):
    if not add_customuser(request.user):
        raise PermissionDenied
    if request.method == 'POST':
        form = UtilisateurForm(request.POST, instance=CustomUser())
        form.fields["groups"].queryset = Group.objects.exclude(Q(customgroup=None) | Q(name__in=SYSTEM_PROFILES))
        if form.is_valid():
            if( request.POST['action'] == 'Enregistrer'):
                form.instance.c_create(form.cleaned_data['groups'])
                messages.add_message(request, messages.INFO, 'Création effectuée avec succès', extra_tags='alert-success')
                return HttpResponseRedirect(add_name(get_dirname(request.get_full_path()), str(form.instance.id)))
    else:
        form = UtilisateurForm()
        form.fields["groups"].queryset = Group.objects.exclude(Q(customgroup=None) | Q(name__in=SYSTEM_PROFILES))
    context = {
        'form': form,
        'instance':form.instance,
        'active_utilisateurs':True,
        'parent_template':form_path_template
    }
    return render(request, 'aptusadmin/utilisateur/utilisateur-creer.html', context)

@login_required
@valid_session
def utilisateur_modifier(request, **kwargs):
    if not change_customuser(request.user):
        raise PermissionDenied    
    instance = CustomUser.objects.get(pk=kwargs['utilisateur_id'])
    
    if request.method == 'POST':
        form = UtilisateurForm(request.POST, instance=instance)
        form.fields["groups"].queryset = Group.objects.exclude(Q(customgroup=None) | Q(name__in=SYSTEM_PROFILES))
        if request.POST['action'] == 'Enregistrer_password':
            if request.POST.get('new_password') == request.POST.get('confirmation_password'):
                # form.instance.set_password(request.POST['new_password'])
                form.instance.pwd_gen(request.POST['new_password'])
                form.instance.save()
                messages.add_message(request, messages.INFO, "Mot de passe modifié avec succès.", extra_tags='alert-success')
                return HttpResponseRedirect(get_dirname(request.get_full_path()))
            else:
                messages.add_message(request, messages.INFO, "Les deux mots de passe ne correspondent pas.", extra_tags='alert-danger')
                return HttpResponseRedirect(request.get_full_path())
        if form.is_valid():
            print('form is valid')
            if request.POST['action'] == 'Enregistrer':
                cleaned_groups = form.cleaned_data['groups']
                form.instance.c_change(groups=cleaned_groups, update_fields=form.changed_data)
                return HttpResponseRedirect(get_dirname(request.get_full_path()))
    else:
        form = UtilisateurForm(instance=instance)
        form.fields["groups"].queryset = Group.objects.exclude(Q(customgroup=None) | Q(name__in=SYSTEM_PROFILES))
    context = {
        'form': form,
        'instance':instance,
        'active_utilisateurs':True,
        'parent_template':form_path_template
    }    
    return render(request, 'aptusadmin/utilisateur/utilisateur-modifier.html', context)


@login_required
def back_to_original_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    primary_user = get_user_model().objects.get(id=request.session['primary_user'])
    request.session['primary_user'] = None
    user.switch_account(request, primary_user)
    return redirect(reverse('aptusadmin:utilisateurs'))


@login_required
@valid_session
def groupes(request):    
    if not viewlist_customgroup(request.user):
        raise PermissionDenied
    CustomPermission.update_permissions_names()
    queryset, btn_filter_list = CustomGroup.c_list(request.GET, request.get_full_path())
    paginator = Paginator(queryset, number_by_page)
    if request.GET.get('page'):
        page = request.GET.get('page')
    else:
        page=1  
    try:
        queryset_per_page = paginator.page(page)
    except PageNotAnInteger:
        queryset_per_page = paginator.page(1)
    except EmptyPage:
        queryset_per_page = paginator.page(paginator.num_pages)
    if request.method == 'POST':
        if request.POST['action'] == 'Supprimer':
            for elt in request.POST.getlist('Choix[]'):
                objet =CustomGroup.objects.get(pk=elt)
                objet.c_delete()
            return HttpResponseRedirect(request.get_full_path())

    filterform = GroupeFilterForm(initial=request.GET)
    
    context = {
        'total':queryset.count(),
        'queryset':queryset_per_page,
        'last_elt_in_page':((int(page)-1)*number_by_page)+len(queryset_per_page),
        'first_elt_in_page':((int(page)-1)*number_by_page)+1,
        'btn_filter_list':btn_filter_list,
        'instance':CustomGroup(),
        'can_add':add_customgroup(request.user),
        'can_delete':delete_customgroup(request.user),
        'enable_filter':True,
        'display_btn_plus':True,
        'filterform':filterform,
        'active_groupes':True,
        'can_import_permission':import_permission(request.user),
        'can_export_permission':export_permission(request.user),
        'parent_template':list_path_template
    }
    return render(request, 'aptusadmin/groupe/groupe-liste.html', context)

@login_required
@valid_session
def groupe_consulter(request, **kwargs):     
    if not view_customgroup(request.user):
        raise PermissionDenied   
    instance = CustomGroup.objects.get(pk=kwargs['groupe_id'])
    prev, next, num_instance, total_instance= CustomGroup.objects.get_prev_and_next_items(instance, CustomGroup.c_list(request.GET, request.get_full_path())[0])
    if request.method == 'POST':
        if( request.POST['action'] == 'Supprimer'):
            message=instance.c_delete()
            messages.add_message(request, messages.INFO, message[1], extra_tags='alert-'+message[0])
            return HttpResponseRedirect(get_dirname(request.get_full_path()))
    display_btn_plus = True if delete_customgroup(request.user) else False
    context = {
        'instance':instance,
        'prev':prev,'next': next , 
        'num_instance': num_instance, 
        'total_instance': total_instance,
        'can_add':add_customgroup(request.user),
        'can_delete':delete_customgroup(request.user),
        'can_change':change_customgroup(request.user),
        'active_groupes':True,
        'display_btn_plus':display_btn_plus,
        'can_export_permission':export_permission(request.user),
        'parent_template':view_path_template
    }    
    return render(request, 'aptusadmin/groupe/groupe-consulter.html', context)

@login_required
@valid_session
def groupe_creer(request, **kwargs):
    if not add_customgroup(request.user):
        raise PermissionDenied       
    V = Q()
    for elt in INSTALLED_APTUS_APPS:
        V = V | Q(content_type__app_label=elt)
    if request.method == 'POST':
        form = GroupeForm(request.POST,instance=CustomGroup())
        form.fields["permissions"].queryset = CustomPermission.objects.filter(V)
        if form.is_valid():
            if( request.POST['action'] == 'Enregistrer'):
                objet,mess=form.instance.c_create(form.cleaned_data["permissions"])
                message = messages.add_message(request, messages.INFO, mess[1], extra_tags='alert-'+mess[0])
                if mess[0] == 'success':
                    return HttpResponseRedirect(add_name(get_dirname(request.get_full_path()), str(objet.id)))
    else:
        form = GroupeForm()
        form.fields["permissions"].queryset = CustomPermission.objects.filter(V)
    context = {
        'form': form,
        'instance':form.instance, 
        'active_groupes':True,
        'parent_template':form_path_template,
    }
    return render(request, 'aptusadmin/groupe/groupe-creer.html', context)

@login_required
@valid_session
def groupe_modifier(request, **kwargs):
    if not change_customgroup(request.user):
        raise PermissionDenied       
    
    V = Q()
    for elt in INSTALLED_APTUS_APPS:
        V = V | Q(content_type__app_label=elt)    
    instance = CustomGroup.objects.get(pk=kwargs['groupe_id'])
    if request.method == 'POST':
        form = GroupeForm(request.POST,instance=instance)
        form.fields["permissions"].queryset = CustomPermission.objects.filter(V)
        if form.is_valid():
            if( request.POST['action'] == 'Enregistrer'):
                liste_perm = []
                objet,message=form.instance.c_change(form.cleaned_data["permissions"]) 
                messages.add_message(request, messages.INFO, message[1], extra_tags='alert-'+message[0])       
                return HttpResponseRedirect(get_dirname(request.get_full_path()))
    else:
        form = GroupeForm(instance=instance)
        form.fields["permissions"].queryset = CustomPermission.objects.filter(V)
        
    context = {
        'form': form,
        'instance':instance,
        'active_groupes':True,
        'parent_template':form_path_template
    }    
    return render(request, 'aptusadmin/groupe/groupe-modifier.html', context)


@login_required
def messages_liste(request):
    queryset = Message.objects.filter(user = request.user).order_by('-id')
    paginator = Paginator(queryset,number_by_page)
    if request.GET.get('page'):
        page = request.GET.get('page')
    else:
        page=1  
    try:
        queryset_per_page = paginator.page(page)
    except PageNotAnInteger:
        queryset_per_page = paginator.page(1)
    except EmptyPage:
        queryset_per_page = paginator.page(paginator.num_pages)
    if request.method == 'POST':
        if( request.POST['action'] == 'Supprimer'):
            for elt in request.POST.getlist('Choix[]'):
                objet =Message.objects.get(pk=elt)
                objet.c_delete()
            return HttpResponseRedirect(request.get_full_path())
    app_name = request.path.split("/")[1]
    context = {
        'total':queryset.count(),
        'queryset':queryset_per_page,
        'last_elt_in_page':((int(page)-1)*number_by_page)+len(queryset_per_page),
        'first_elt_in_page':((int(page)-1)*number_by_page)+1,
        'instance':Message(),
        'display_btn_plus':True,
        'active_accueil':True,
        'can_delete':True,
    }
        
    return render(request, app_name + '/message-liste.html', context)


@login_required
def message_consulter(request, message_id):
    instance = Message.objects.get(pk=message_id)
    if instance.statut == False:
        instance.statut =True
        instance.save()
    prev, next, num_instance, total_instance= Message.objects.get_prev_and_next_items(instance, Message.objects.filter(user = request.user).order_by('-id'))    
    if request.method == 'POST':
        if( request.POST['action'] == 'Supprimer'):
            instance.c_delete()
            return HttpResponseRedirect(get_dirname(request.get_full_path()))
    app_name = request.path.split("/")[1]
    context = {
        'instance':instance,
        'prev':prev,'next': next , 
        'num_instance': num_instance, 
        'total_instance': total_instance,
        'active_accueil':True,
    }
    return render(request, app_name + '/message-consulter.html', context)

@login_required
@valid_session
def utilisateurs_view(request):
    return render(request, 'aptusadmin/consulter_utilisateur-liste.html', {'utilisateurs':get_user_model().objects.all().exclude(username='aptusadm')})

@login_required
@valid_session
def logentry_liste(request):
    queryset, btn_filter_list = CustomLogEntry.c_list(params=request.GET, full_path=request.get_full_path())
    paginator = Paginator(queryset,number_by_page)
    if request.GET.get('page'):
        page = request.GET.get('page')
    else:
        page=1  
    try:
        queryset_per_page = paginator.page(page)
    except PageNotAnInteger:
        queryset_per_page = paginator.page(1)
    except EmptyPage:
        queryset_per_page = paginator.page(paginator.num_pages)
    context = {
        'total':queryset.count(),
        'queryset':queryset_per_page,
        'last_elt_in_page':((int(page)-1)*number_by_page)+len(queryset_per_page),
        'first_elt_in_page':((int(page)-1)*number_by_page)+1,
        'display_btn_plus':True,
        'can_delete':True,
        'instance':CustomLogEntry(),
        'btn_filter_list':btn_filter_list,
        'enable_filter':True,
        'filterform':LogEntryFilterForm(initial=request.GET),
        'active_logentry':True,
        'parent_template':list_path_template
    }
        
    return render(request, 'aptusadmin/logentry-liste.html', context)


@login_required
def alert_liste(request):
    # Old > to be removed (Used in AptusPark)
    queryset = Alert.c_list()
    parent_template = request.path.split("/")[1]+'/main/first.html' 
    context = {
        'queryset':queryset,
        'display_btn_plus':True,
        'can_delete':True,
        'instance':Alert(),
        'active_accueil':True,
        'parent_template':parent_template
    }

    return render(request, 'aptusadmin/alert-liste.html', context)


@login_required
def alert_list(request):
    # New method used in Aptus E-Learn (New logic that we have adapted the last time we updated messages view)
    queryset = Alert.c_list()
    app_name = request.path.split("/")[1]
    context = {
        'alerts': queryset,
        'instance': Alert(),
    }
    return render(request, app_name + '/alert-list.html', context)


@login_required
def get_message(request):
    user = request.user
    messages = user.get_massages()[1]
    json_messages=serializers.serialize("json", list(messages))
    return  JsonResponse(json_messages, safe=False )

@login_required
def get_nbr_message(request):
    dict={}
    user = request.user
    nbr_messages = user.get_massages()[0]
    dict['nbr']=nbr_messages
    return HttpResponse(json.dumps(dict), content_type='application/json')

