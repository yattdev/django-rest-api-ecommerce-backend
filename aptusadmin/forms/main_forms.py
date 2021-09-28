# -*- coding: utf-8 -*-
from django import forms
from django.forms import widgets
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm, TextInput, SelectMultiple, Textarea, PasswordInput, EmailInput
from django.db.models import Q

from aptusadmin.models import *
from aptusadmin import settings as aptusadmin_settings


class ConnexionForm(forms.Form):
    username = forms.CharField(max_length=30,widget=forms.TextInput(attrs={'class': 'form-control  ','placeholder':"Identifiant",'required':'true'}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Mot de passe','required':'true'}))

class Change_password(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','required':'true'}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','required':'true'}))
    confirmation_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','required':'true'}))

class UtilisateurForm(ModelForm):
    est_active_choix = (
        ('', '-------------'),              
        ('Non', 'Non'),
        ('Oui', 'Oui'),
        )     
    #est_actif=forms.CharField(widget=forms.Select(choices=est_active_choix,attrs={'class': 'form-control '}))

    class Meta:
        model = CustomUser
        fields = [
            'last_name', 'first_name', 'username', 'groups', 'is_active',
            'email', 'google_account', 'microsoft_account'
        ]
        widgets = {
            'last_name':TextInput(attrs={'class': 'form-control'}),
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'username': TextInput(attrs={'class': 'form-control'}),
            'groups': SelectMultiple(attrs={'class': 'form-control select2_demo_2'}),
            'email': EmailInput(attrs={'class': 'form-control'}),
            'google_account': EmailInput(attrs={'class': 'form-control'}),
            'microsoft_account': EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if self.instance.id and 'last_name' in self.changed_data and set(SYSTEM_PROFILES).intersection(set(self.instance.groups.all().values_list('name', flat=True))):
            raise forms.ValidationError(f"Vous n'êtes pas autorisés à modifier le nom d'un utilisateur appartenant à la liste des groupes: {SYSTEM_PROFILES}")
        return last_name

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if self.instance.id and 'first_name' in self.changed_data and set(SYSTEM_PROFILES).intersection(set(self.instance.groups.all().values_list('name', flat=True))):
            raise forms.ValidationError(f"Vous n'êtes pas autorisés à modifier le prénom d'un utilisateur appartenant à la liste des groupes: {SYSTEM_PROFILES}")
        return first_name

    def clean_google_account(self):
        google_account = self.cleaned_data.get('google_account')
        is_valid = False
        if google_account:
            for suffix in aptusadmin_settings.GOOGLE_ACCOUNT_SUFFIXES:
                if google_account.endswith(suffix):
                    is_valid = True
                    break
        if not is_valid and google_account:
            raise forms.ValidationError('Saisissez une adresse e-mail valide.')
        if (
            google_account and 'google_account' in self.changed_data and
            CustomUser.objects.filter(google_account=google_account).exists()
        ):
            raise forms.ValidationError(["Un utilisateur avec ce compte Google existe déjà."])
        return google_account

    def clean_microsoft_account(self):
        microsoft_account = self.cleaned_data.get('microsoft_account')
        is_valid = False
        if microsoft_account:
            for suffix in aptusadmin_settings.MICROSOFT_ACCOUNT_SUFFIXES:
                if microsoft_account.endswith(suffix):
                    is_valid = True
                    break
        if not is_valid and microsoft_account:
            raise forms.ValidationError('Saisissez une adresse e-mail valide.')
        if (
            microsoft_account and 'microsoft_account' in self.changed_data and
            CustomUser.objects.filter(microsoft_account=microsoft_account).exists()
        ):
            raise forms.ValidationError(["Un utilisateur avec ce compte Microsoft existe déjà."])
        return microsoft_account

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and 'email' in self.changed_data and User.objects.filter(email=email).exists():
            raise forms.ValidationError(["Un utilisateur avec cet email existe déjà."])
        return email

"""class UtilisateurCreerForm(UtilisateurForm):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','required':'true'}))
    confirmation_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','required':'true'}))"""

class UtilisateurFilterForm(forms.Form): 
    nom = forms.CharField(label='Nom',widget=forms.TextInput(attrs={'class': 'form-control'}),required=False) 
    prenom = forms.CharField(label='Prénom',widget=forms.TextInput(attrs={'class': 'form-control'}),required=False) 
    identifiant = forms.CharField(label='Identifiant',widget=forms.TextInput(attrs={'class': 'form-control'}),required=False) 
    groupe = forms.ModelChoiceField(label='Groupe', queryset=Group.objects.exclude(customgroup=None),widget=forms.Select(attrs={'class': 'form-control'}),required=False)
    exclude_groupe = forms.BooleanField(label='Exclude', required=False)

class GroupeForm(ModelForm):
    class Meta:
        model = CustomGroup
        fields = ['name','description','permissions'] 
        widgets = {'name':TextInput(attrs={'class': 'form-control'}),
                   'description': Textarea(attrs={'class': 'form-control', 'rows':'5'}),
                   'permissions': SelectMultiple(attrs={'class': 'form-control'})
                   }         
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if 'name' in self.changed_data and self.instance.name in SYSTEM_PROFILES:
            raise forms.ValidationError(f"Vous n'êtes pas autorisés à modifier le nom d'un groupe système")
        return name

class GroupeFilterForm(forms.Form): 
    nom=forms.CharField(label='Nom',widget=forms.TextInput(attrs={'class': 'form-control'}),required=False) 

class LogEntryFilterForm(forms.Form): 
    nom = forms.CharField(label="Nom d'utilisateur",widget=forms.TextInput(attrs={'class': 'form-control'}),required=False) 
    identifiant = forms.CharField(label="Identifiant",widget=forms.TextInput(attrs={'class': 'form-control'}),required=False) 
    type_contenu=forms.ModelChoiceField(label="Type de contenu", queryset=ContentType.objects.filter(Q(app_label='educat')|Q(app_label='aptusadmin')),widget=forms.Select(attrs={'class': 'form-control', 'style':'margin-bottom:4px'}), required=False)
    contenu = forms.CharField(label="Contenu",widget=forms.TextInput(attrs={'class': 'form-control'}),required=False)     
    date_min=forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y',attrs={'class': 'form-control','placeholder':'dd/mm/yyyy'}),input_formats=('%d/%m/%Y',),required=False)
    date_max = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y',attrs={'class': 'form-control','placeholder':'dd/mm/yyyy'}),input_formats=('%d/%m/%Y',),required=False)


class PasswordResetForm(forms.Form):

    def __init__(self, *arg, **kwargs):
        super(PasswordResetForm, self).__init__(*arg)
        if 'form_type' in kwargs:
            form_type = kwargs.pop('form_type')
            if form_type == 'email_form':
                self.fields['new_password'].required = False
                self.fields['confirmation_password'].required = False
            elif form_type == 'pwd_form':
                self.fields['email'].required = False

    new_password = forms.CharField(
        label='Nouveau mot de passe', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    confirmation_password = forms.CharField(
        label='Confirmation du mot de passe', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    email = forms.EmailField(label='Adresse mail', widget=forms.EmailInput(attrs={'class': 'form-control'}))

    def clean(self):
        if ('new_password' in self.cleaned_data and 'confirmation_password' in self.cleaned_data and
                self.cleaned_data['new_password'] != '' and self.cleaned_data['confirmation_password'] != ''):
            new_pass = self.cleaned_data['new_password']
            conf_pass = self.cleaned_data['confirmation_password']
            if new_pass != conf_pass:
                self.errors['confirmation_password'] = self.error_class(['Les deux mots de passe ne corresponds pas!'])

        if 'email' in self.cleaned_data and self.cleaned_data['email'] != '':
            users = CustomUser.objects.filter(email=self.cleaned_data['email'], email_is_valid=True)
            if users.count() == 0:
                self.errors['email'] = self.error_class(
                    ["Cette adresse mail n'existe pas dans notre base de données ou elle n'a pas été vérifiée."])


#######################
#  Label forms
#######################
class LabelForm(forms.ModelForm):

    def __init__(self, available_labels=None, *args, **kwargs):
        super(LabelForm, self).__init__(*args, **kwargs)
        if available_labels is not None:
            self.fields['parent'].queryset = available_labels

    class Meta:
        model = Label
        fields = ['label', 'parent', 'color']
        widgets = {
            'label': widgets.TextInput(attrs={'class': 'form-control'}),
            'parent': widgets.Select(attrs={'class': 'form-control'}),
            'color': widgets.TextInput(attrs={'class': 'form-control'}),
        }
