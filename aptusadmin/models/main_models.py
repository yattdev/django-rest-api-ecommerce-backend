# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from furl import furl

from django.contrib.auth import login
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from django.db import models, IntegrityError
from django.contrib.auth.models import AbstractUser, Group, Permission, User
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

from aptusadmin.utils import MyappsManager, CustomUserManager, password_generator, username_generator
from aptusadmin.settings import ROOT_ID, SIGNATAIRE_MAIL, NOM_SOLUTION, TOKEN_VALIDATION_TIME, SYSTEM_PROFILES, \
    REJECTED_USERNAME_PREFIXES, INSTALLED_APPS


class CustomPermission(Permission):
    class Meta:
        proxy = True
        ordering = ['id']
        default_permissions = ()

    @classmethod
    def update_permissions_names(cls):
        for installed_app in INSTALLED_APPS:
            app_models = apps.get_app_config(installed_app).get_models()
            for model in app_models:
                content_type = ContentType.objects.get(app_label=installed_app, model=model._meta.model_name)
                for codename, name in model._meta.permissions:
                    Permission.objects.update_or_create(
                        content_type=content_type,
                        codename=codename,
                        defaults={
                        'name': name
                    })
        return True, ('success', 'Les noms des permissions ont été modifiés avec succès.')


class CustomGroup(Group):
    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view','viewlist', 'managepermissions')
        verbose_name_plural = "Groupes"
    
    objects=MyappsManager()  
    description = models.TextField('Description', blank=True, default='')  
    def meta(self):
        return self._meta
    def c_create(self, permissions):
        self.name = self.name.upper()
        self.save()   
        self.permissions.set(permissions)
        message = ("success", "Création effectuée avec succès")
        return self, message
    def c_change(self, permissions):
        self.save() 
        self.permissions.set(permissions)
        message = ("success", "Modification effectuée avec succès")  
        return self,message
    
    def c_delete(self):
        self.delete()
        message = ("success", "Suppression effectuée avec succès")
        return message
    def get_permissions(self):
        return CustomPermission.objects.filter(group=self)
    def get_utilisateurs(self):    
        return CustomUser.objects.filter(groups=self)
    @classmethod
    def c_list(cls, params, full_path):
        dict = {}; btn_list = []
        if params:
            try:
                dict['name__icontains'] = params['nom']
                btn = {}
                btn['label'] = "Nom contient " + '"'+ params['nom'] + '"'
                btn['link'] = full_path.replace("nom=" + params['nom'], '')
                btn_list.append(btn)
            except KeyError:
                pass

        return cls.objects.filter(**dict), btn_list 


class CustomUser(AbstractUser):    
    class Meta:
        ordering = ['-last_name', '-first_name']
        default_permissions = ('add', 'change', 'delete', 'view','viewlist','importpermission', 'exportpermission')
        verbose_name_plural = "Utilisateurs"

    must_change_pwd = models.BooleanField(default=False)
    tmp_pwd = models.CharField('Mot de passe temporaire', max_length=10, default='', blank=True)
    email_is_valid = models.BooleanField(default=False)
    token_valid = models.BooleanField(default=False)
    old_passwords = models.CharField('Anciens mots de passe', max_length=255, default='', blank=True)
    last_password_change_date = models.DateTimeField('Dernière date de changement de mot de pass', null=True, blank=True)
    session = models.CharField('Session', max_length=300, default='', blank=True)
    avatar = models.ImageField("Avatar", upload_to='user/avatar', null=True, blank=True)
    google_account = models.EmailField('Compte Google', unique=True, null=True, blank=True)
    microsoft_account = models.EmailField('Compte Microsoft', unique=True, null=True, blank=True)

    myapps_manager = CustomUserManager()

    def meta(self):
        return self._meta

    def __str__(self):
        return self.last_name + ' ' + self.first_name

    def c_create(self, groups=[], pwd='', auto_gen_username=False):

        res = True
        message = ("success", "Création effectuée avec succès.")
        if not auto_gen_username:
            invalid_prefix = ''
            for prefix in REJECTED_USERNAME_PREFIXES:
                if self.username.startswith(prefix):
                    invalid_prefix = prefix
                    break
            if invalid_prefix != '':
                message = ('danger', f"La chaîne de caractères '{prefix}' est interdite en début de l'identifiant.")
                res = False
        if res:
            try:
                # self.old_passwords = f"'{pwd}', "
                self.username = self.username.lower()
                self.pwd_gen(pwd)  # Attribue un mot de passe temporaire et sauvegarde l'instance
                self.groups.set(groups)
            except IntegrityError:
                message = ('danger', "Un utilisateur avec le même identifiant existe déjà.")
                res = False

        return res, message

    def c_delete(self):
        self.delete()

    def c_change(self, groups=[], update_fields=[], auto_gen_username=False):
        
        res = True
        message = ("success", "Modification effectuée avec succès.")
        self.username = self.username.lower()

        if 'email' in update_fields:
            if User.objects.filter(email=self.email).exists():
                raise Exception("Un utilisateur avec cet email existe déjà.")
            self.email_is_valid = False
        try:
            if not auto_gen_username and self.username != CustomUser.objects.get(id=self.id).username:
                invalid_prefix = ''
                for prefix in REJECTED_USERNAME_PREFIXES:
                    if self.username.startswith(prefix):
                        invalid_prefix = prefix
                        break
                if invalid_prefix != '':
                    message = ('danger', f"La chaîne de caractères '{prefix}' est interdit au début d'identifiant.")
                    res = False

            if res:
                self.save()
                
                old_groups = self.groups.all()
                removed_system_groups = [
                    group for group in old_groups if group not in groups and group.name in SYSTEM_PROFILES
                ]
                groups = list(groups) + removed_system_groups

                self.groups.set(groups)
        except IntegrityError:
            message = ('danger', "Un utilisateur avec le même identifiant existe déjà.")
            res = False
        return res, message

    def get_massages(self):
        massages = Message.objects.filter(user=self, statut = False).order_by('-date_reception')
        return (massages.count(),massages[0:5])

    def get_alerts(self):
        user_filter = models.Q(user=self) | models.Q(groupe__in=self.groups.all())
        return Alert.c_list().filter(user_filter)

    def get_customgroups(self):
        return CustomGroup.objects.filter(user=self)

    def get_permissions(self):
        return CustomPermission.objects.filter(user=self)

    def switch_account(self, request, user):
        login(request, user)

    def pwd_gen(self, default_pwd=''):
        if default_pwd != '':
            self.tmp_pwd = default_pwd
        else:
            self.tmp_pwd = password_generator(10)
        self.must_change_pwd = True
        self.set_password(self.tmp_pwd)
        self.save()
        if self.email and self.email_is_valid:
            message = ("Bonjour {} {}, \n\n" +
                        "Votre mot de passe d'accès à la plateforme AptusEducat a été réinitialisé avec succès. \n" +
                        "Le nouveau mot de passe temporaire est: {} \n" +
                        "Vous pouvez le modifier en vous connectant à la plateforme {}. \n\n" +
                        "Cordialement.\n{}").format(self.first_name, self.last_name, self.tmp_pwd, NOM_SOLUTION, SIGNATAIRE_MAIL)

            send_mail(
                'Réinitialisation de votre mot de passe '+ NOM_SOLUTION,
                message,
                'support@aptus.ma',
                [self.email],
                fail_silently=True,
            )
        return self

    def send_mail_activation_link(self, domain):

        from aptusadmin.tokens import account_activation_token

        user = self.user_ptr
        mail_subject = "Confirmation de votre email pour AptusEducat"
        message = render_to_string('aptusadmin/email_validation/activation_email.html', {
            'user': self,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'mail': urlsafe_base64_encode(force_bytes(self.email)),
            'token': account_activation_token.make_token(user),
            'token_creation_date': urlsafe_base64_encode(force_bytes(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))),
        })
        send_mail(
            mail_subject,
            message,
            'support@aptus.ma',
            [self.email],
            fail_silently=False,
        )
        message = 'success', 'Un lien de confirmation vous a été envoyé par email,' \
                  ' il vous suffit de cliquer dessus pour valider votre adresse email.'
        return True, message

    def activate_mail_adress(self, token, mail, token_creation_date):

        from aptusadmin.tokens import account_activation_token

        token_created_at = datetime.strptime(token_creation_date, "%m/%d/%Y %H:%M:%S")
        token_experation_date = token_created_at + timedelta(hours=TOKEN_VALIDATION_TIME)

        if token_experation_date < datetime.now():
            message = 'danger', "Opération impossible. Ce lien d'activation a expiré."
            res = False
        else:
            if account_activation_token.check_token(self.user_ptr, token):
                self.email_is_valid = True
                self.email = mail
                self.save()
                message = 'success', 'Votre adresse email a été activée avec succès.'
                res = True
            else:
                message = 'danger', "Opération impossible. Ce lien d'activation est déjà utilisé."
                res = False
        return res, message

    def send_password_reset_mail(self, domain):

        from aptusadmin.tokens import password_reset_token

        user = self.user_ptr
        mail_subject = 'Demande de réinitialisation de votre mot de passe AptusEducat.'
        message = render_to_string('aptusadmin/email_validation/password_reset_mail.html', {
            'user': self,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': password_reset_token.make_token(user),
            'token_creation_date': urlsafe_base64_encode(force_bytes(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))),
        })
        send_mail(
            mail_subject,
            message,
            'support@aptus.ma',
            [self.email],
            fail_silently=False,
        )
        if not self.token_valid:
            self.token_valid = True
            self.save()
        message = 'success', (
            'Les instructions pour la réinitialisation de votre mot de passe vous ont été envoyés par e-mail. '
            'Si vous ne recevez pas notre e-mail dans votre boite de réception, pensez à vérifier dans vos courriers indésirables !'
        )
        return True, message

    def check_token_validity(self, token, token_creation_date):

        from aptusadmin.tokens import password_reset_token

        token_created_at = datetime.strptime(token_creation_date, "%m/%d/%Y %H:%M:%S")
        token_experation_date = token_created_at + timedelta(hours=TOKEN_VALIDATION_TIME)

        if token_experation_date < datetime.now():
            message = 'danger', "Opperation impossible. Ce token a expiré."
            res = False
        else:
            if password_reset_token.check_token(self.user_ptr, token) and self.token_valid:
                message = 'success', 'Votre lien est valide.'
                res = True
            else:
                message = 'danger', "Ce token est déjà utilisé."
                res = False
        return res, message

    def reset_password(self, password, permanent=False):
        self.set_password(password)
        self.token_valid = False
        if permanent and self.must_change_pwd:
            self.must_change_pwd = False
        self.save()

    @classmethod
    def generate_username(cls, length=6):
        valid_username = False
        while not valid_username:
            username = username_generator(length)
            try:
                cls.objects.get(username=username)
            except ObjectDoesNotExist:
                valid_username = True
        return username

    @classmethod
    def c_list(cls, params, full_path):
        dict, btn_list, exclude_dict = {}, [], {}
        if params:
            try:
                dict['last_name__icontains'] = params['nom']
                btn = {}
                f = furl(full_path)
                btn['label'] = "Nom contient " + '"'+ params['nom'] + '"'
                btn['link'] = f.remove(['nom']).url
                btn_list.append(btn)
            except KeyError:
                pass
            
            try:
                dict['first_name__icontains'] = params['prenom']
                btn = {}
                f = furl(full_path)
                btn['label'] = "Prénom contient " + '"'+ params['prenom'] + '"'
                btn['link'] = f.remove(['prenom']).url
                btn_list.append(btn)
            except KeyError:
                pass

            try:
                dict['username__icontains'] = params['identifiant']
                btn = {}
                f = furl(full_path)
                btn['label'] = "Identifiant contient " + '"'+ params['identifiant'] + '"'
                btn['link'] = f.remove(['identifiant']).url
                btn_list.append(btn)
            except KeyError:
                pass

            try:
                dict['groups'] = Group.objects.get(pk=params['groupe'])
                btn = {}
                f = furl(full_path)
                btn['label'] = "Groupe égal " + '"'+ str(dict['groups']) + '"'
                
                exclude = params.get('exclude_groupe', False)
                if exclude:
                    del dict['groups']
                    exclude_dict['groups'] = Group.objects.get(pk=params['groupe'])
                    btn['label'] = "Groupe différent de " + '"'+ str(exclude_dict['groups']) + '"'
                    btn['link'] = f.remove(['exclude_groupe']).url

                btn['link'] = f.remove(['groupe']).url
                btn_list.append(btn)
            except KeyError:
                pass
            
        return cls.objects.filter(**dict).exclude(id=ROOT_ID).exclude(**exclude_dict), btn_list 


class Message(models.Model):  

    class Meta:
        verbose_name_plural = "Boite de reception"
        default_permissions = ()

    user = models.ForeignKey(CustomUser, related_name="recipient", on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, default=1, blank=True, related_name="sender", on_delete=models.PROTECT)
    subject = models.CharField('Sujet', max_length=256)
    content = models.TextField()
    date_reception = models.DateTimeField('Date de réception')
    statut = models.BooleanField('Lu', default=False)
    notified_by_mail = models.BooleanField(default=False)
    objects = MyappsManager()

    def meta(self):
        return self._meta

    def __str__(self):
        return self.subject

    def c_create(self, notify_by_email=False):

        self.save()
        
        if notify_by_email:
            self.notify_by_email()

    def c_delete(self):
        for elt in Attachment.objects.filter(message=self):
            elt.c_delete()
        self.delete()

    def notify_by_email(self):
        if self.user.email and self.user.email_is_valid:
            try:
                html_content = self.content
                msg = EmailMessage(self.subject, html_content, 'support@aptus.ma', [self.user.email])
                msg.content_subtype = "html"
                msg.send()
                self.notified_by_mail = True
                self.save()
            except:
                pass


class Attachment(models.Model): 
    class Meta:
        default_permissions = () 
    file=models.FileField(upload_to='attachments',blank=True,null=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    def c_create(self):
        self.save()
    def c_delete(self):
        self.file.delete()
        self.delete()


class CustomLogEntry(LogEntry):
    class Meta:
        default_permissions = ('viewlist',)
        verbose_name_plural = "Journal d'activités"
        proxy = True
        ordering = ['-id']
    objects = MyappsManager()
    def meta(self):
        return self._meta
    @classmethod
    def c_list(cls, params, full_path):
        dict = {}; btn_list = []
        if params:
            try:
                dict['user__last_name__icontains'] = params['nom']
                if full_path:
                    btn = {}; f = furl(full_path)
                    btn['label'] = "Nom d'utilisateur contient " + '"'+ params['nom'] + '"'
                    btn['link'] = f.remove(['nom']).url
                    btn_list.append(btn)
            except KeyError:
                pass
            try:
                dict['user__username__icontains'] = params['identifiant']
                if full_path:
                    btn = {}; f = furl(full_path)
                    btn['label'] = "Identifiant contient " + '"'+ params['identifiant'] + '"'
                    btn['link'] = f.remove(['identifiant']).url
                    btn_list.append(btn)
            except KeyError:
                pass
            try:
                dict['content_type'] = ContentType.objects.get(pk=params['type_contenu'])
                if full_path:
                    btn = {}; f = furl(full_path)
                    btn['label'] = "Type de  contenu égale" + '"'+ str(dict['content_type']) + '"'
                    btn['link'] = f.remove(['type_contenu']).url
                    btn_list.append(btn)
            except KeyError:
                pass
            try:
                dict['object_repr__icontains'] = params['contenu']
                if full_path:
                    btn = {}; f = furl(full_path)
                    btn['label'] = "Contenu contient" + '"'+ params['contenu'] + '"'
                    btn['link'] = f.remove(['contenu']).url
                    btn_list.append(btn)

            except KeyError:
                pass
            if 'date_min' in params and 'date_max' in params:
                dict['action_time__gte'] = datetime.strptime(params['date_min'], "%d/%m/%Y")
                dict['action_time__lte'] = datetime.strptime(params['date_max'], "%d/%m/%Y")
                if full_path:
                    btn = {}; f = furl(full_path)
                    btn['label'] = "Date entre " + '"'+ params['date_min'] + " et " + params['date_max'] + '"'
                    btn['link'] = f.remove(['date_min','date_max']).url
                    btn_list.append(btn)
            elif 'date_min' in params:
                dict['action_time__gte'] = datetime.strptime(params['date_min'], "%d/%m/%Y")
                if full_path:
                    btn = {}; f = furl(full_path)
                    btn['label'] = "Date supérieur à " + '"'+ params['date_min'] + '"'
                    btn['link'] = f.remove(['date_min']).url
                    btn_list.append(btn)
            elif 'date_max' in params:
                dict['action_time__lte'] = datetime.strptime(params['date_max'], "%d/%m/%Y")
                if full_path:
                    btn = {}; f = furl(full_path)
                    btn['label'] = "Date inférieure à " + '"'+ params['date_max'] + '"'
                    btn['link'] = f.remove(['date_max']).url
                    btn_list.append(btn)

        return cls.objects.filter(**dict), btn_list


class Alert(models.Model):
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE)
    groupe = models.ForeignKey(CustomGroup, null=True, blank=True, on_delete=models.CASCADE)
    categorie = models.TextField(default='')  # ex: {'annee': 2020, 'appli': 'educat', ...}
    subject = models.TextField('Sujet')
    created_at = models.DateTimeField("Date et heure de création")
    link = models.CharField(max_length=256, default='', blank=True)

    def __str__(self):
        return self.subject

    @classmethod
    def c_list(cls):
        return cls.objects.all().order_by('-created_at')
