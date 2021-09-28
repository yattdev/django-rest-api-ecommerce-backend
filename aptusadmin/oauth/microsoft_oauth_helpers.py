import os
import json
import pickle

from django.conf import settings

from aptusadmin.settings import MICROSOFT_API_CLIENT_SECRETS_FILE, MICROSOFT_API_ADMIN_SCOPES

# Load the credentials.json file
microsoft_api_settings = {}
if os.path.exists(MICROSOFT_API_CLIENT_SECRETS_FILE):
    with open(MICROSOFT_API_CLIENT_SECRETS_FILE, 'r') as stream:
        microsoft_api_settings = json.load(stream)
        microsoft_api_settings['scopes'] = MICROSOFT_API_ADMIN_SCOPES


def load_microsoft_creds(user, is_admin=True):

    import msal
    
    creds = msal.SerializableTokenCache()
    
    token_dirname = 'admin_credentials' if is_admin else 'credentials'
    token_filename = 'admin_token.pickle' if is_admin else f'token_{user.id}.pickle'
    tokens_dir = os.path.join(settings.BASE_DIR, 'credentials', 'microsoft', token_dirname)
    token_path = os.path.join(tokens_dir, token_filename)

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token_bin:
            token = pickle.load(token_bin)
            creds.deserialize(token)

    return creds


def save_microsoft_creds(user, creds, is_admin=True):
    if creds.has_state_changed:
        token_dirname = 'admin_credentials' if is_admin else 'credentials'
        token_filename = 'admin_token.pickle' if is_admin else f'token_{user.id}.pickle'
        tokens_dir = os.path.join(settings.BASE_DIR, 'credentials', 'microsoft', token_dirname)
        token_path = os.path.join(tokens_dir, token_filename)
        
        if not os.path.exists(tokens_dir):
            os.makedirs(tokens_dir)

        with open(token_path, 'wb') as token:
            pickle.dump(creds.serialize(), token)


def get_msal_app(creds=None):

    import msal

    auth_app = msal.ConfidentialClientApplication(
        microsoft_api_settings['client_id'],
        authority=microsoft_api_settings['authority'],
        client_credential=microsoft_api_settings['client_secret'],
        token_cache=creds
    )

    return auth_app


# Method to generate a sign-in flow
def get_sign_in_flow(is_admin=True):
    auth_app = get_msal_app()
    redirects = microsoft_api_settings['redirect']
    if is_admin:
        redirect_uri = redirects[0] if '/aptusadmin/' in redirects[0] else redirects[1]
    else:
        redirect_uri = redirects[0] if '/enseignant/' in redirects[0] else redirects[1]
    return auth_app.initiate_auth_code_flow(
        microsoft_api_settings['scopes'],
        redirect_uri=redirect_uri
    )


# Method to exchange auth code for access token
def get_token_from_code(request, is_admin=True):
    creds = load_microsoft_creds(request.user, is_admin)
    auth_app = get_msal_app(creds)

    # Get the flow saved in session
    flow = request.session.pop('auth_flow', {})
    result = auth_app.acquire_token_by_auth_code_flow(flow, request.GET)
    save_microsoft_creds(request.user, creds, is_admin)
    return result
