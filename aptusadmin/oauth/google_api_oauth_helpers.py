import os
import pickle

from django.conf import settings

from myapps import settings as myapps_settings


def get_google_creds(user, is_admin=False):

    SCOPES = myapps_settings.GOOGLE_API_ADMIN_SCOPES
    creds = None

    token_dirname = 'admin_credentials' if is_admin else 'credentials'
    token_filename = 'admin_token.pickle' if is_admin else f'token_{user.id}.pickle'
    tokens_dir = os.path.join(settings.BASE_DIR, 'credentials', 'google', token_dirname)
    token_path = os.path.join(tokens_dir, token_filename)

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
            # creds = credentials.Credentials(**creds)

    return creds


def set_google_creds(user, creds, is_admin=False):

    token_dirname = 'admin_credentials' if is_admin else 'credentials'
    token_filename = 'admin_token.pickle' if is_admin else f'token_{user.id}.pickle'
    tokens_dir = os.path.join(settings.BASE_DIR, 'credentials', 'google', token_dirname)
    token_path = os.path.join(tokens_dir, token_filename)
    
    if not os.path.exists(tokens_dir):
        os.makedirs(tokens_dir)

    with open(token_path, 'wb') as token:
        pickle.dump(creds, token)


def remove_google_creds(user, is_admin=False):

    SCOPES = myapps_settings.GOOGLE_API_ADMIN_SCOPES
    creds = None

    token_dirname = 'admin_credentials' if is_admin else 'credentials'
    token_filename = 'admin_token.pickle' if is_admin else f'token_{user.id}.pickle'
    tokens_dir = os.path.join(settings.BASE_DIR, 'credentials', 'google', token_dirname)
    token_path = os.path.join(tokens_dir, token_filename)

    if os.path.exists(token_path):
        os.remove(token_path)
