# -*- coding: utf-8 -*-
import os
import json
from django.conf import settings

ETABLISSEMENT = getattr(settings, 'ETABLISSEMENT', {'nom':'', 'code':''})

TMP_DIR = os.path.join(settings.BASE_DIR, 'tmp') 
rows_per_page = 100
ADMIN_GUIDE='AdminGuide.pdf'
USER_GUIDE="UserGuide.pdf"
ROOT_ID = 1
TOKEN_VALIDATION_TIME = 1  # En heure


def message_content(file):
    message="<p>La sauvegarde de votre base de données a été créée avec succès.</p>"\
            +"<p>Vous pouvez restaurer votre base de données à partir de cette sauvegarde depuis votre console d'administration.</p>"\
            +"<p>Vous pouvez consulter ce guide pour en savoir plus :</p>"\
            +"<p><a href='/static/docs/"+ADMIN_GUIDE+"' target='_blank'> Guide d'administration</a></p>"\
            +"<br><p>Si vous souhaitez conserver la sauvegarde de votre base sur votre ordinateur, vous pouvez la télécharger en cliquant sur ce lien :</p>"\
            +"<p><a href='/backup/"+file+"'>"+file+"</a></p>"\
            +"<p>Cette sauvegarde sera disponible durant 90 jours.</p>"
    return message

def message_subject():
    return "La sauvegarde de votre base est terminée."

PG_PATH = getattr(settings, 'PG_PATH', '/usr/bin')

INSTALLED_APTUS_APPS = getattr(settings, 'INSTALLED_APTUS_APPS', ['aptusadmin'])


initial_updated_by = 1


list_path_template='aptusadmin/main/list.html'
view_path_template='aptusadmin/main/view.html'
form_path_template='aptusadmin/main/form.html'

# Paramètres de réinitialisation du mot de passe
SIGNATAIRE_MAIL = getattr(settings, 'SIGNATAIRE_MAIL', 'Adminstrateur APTUS')
NOM_SOLUTION = getattr(settings, 'NOM_SOLUTION', 'APTUS')

UTC_PLUS = getattr(settings, 'UTC_PLUS', 1)

NAME_CHOICES = getattr(settings, 'NAME_CHOICES', (('', '------'),))

REJECTED_USERNAME_PREFIXES = getattr(settings, 'REJECTED_USERNAME_PREFIXES', [])
SYSTEM_PROFILES = getattr(settings, 'SYSTEM_PROFILES', [])
OLD_PASSWORDS_COUNT = getattr(settings, 'OLD_PASSWORDS_COUNT', 2)

SCREEN_WIDTH_MIN = getattr(settings, 'SCREEN_WIDTH_MIN', 800)

INSTALLED_APPS = getattr(settings, 'INSTALLED_APTUS_APPS', ['aptusadmin', ])

CONNECTION_URL = getattr(settings, 'CONNECTION_URL', '/')  # View to be redirected to after user logged in

VERBOSE_NAME = getattr(settings, 'VERBOSE_NAME', {})


GOOGLE_ACCOUNT_SUFFIXES = getattr(settings, 'GOOGLE_ACCOUNT_SUFFIXES', [
    'gmail.com'
])
MICROSOFT_ACCOUNT_SUFFIXES = getattr(settings, 'MICROSOFT_ACCOUNT_SUFFIXES', [
    'microsoft.com',
    'hotmail.com',
    'live.com',
])


# GOOGLE API related settings
GOOGLE_API_CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, 'credentials', 'google', 'credentials.json')
GOOGLE_API_ADMIN_SCOPES = [
    'https://www.googleapis.com/auth/admin.reports.audit.readonly'
]
GOOGLE_API_REDIRECT_URIS = ''

try:
    with open(GOOGLE_API_CLIENT_SECRETS_FILE, 'r') as creds:
        data = json.load(creds)
        GOOGLE_API_REDIRECT_URIS = data['web']['redirect_uris']
except FileNotFoundError:
    pass


# MICROSOFT API related settings
MICROSOFT_API_CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, 'credentials', 'microsoft', 'credentials.json')
MICROSOFT_API_ADMIN_SCOPES = [
    "user.read",
    "mailboxsettings.read",
    "calendars.readwrite"
]
