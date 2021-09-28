from django.http import HttpResponseRedirect
from django.shortcuts import redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from aptusadmin import settings as aptusadmin_settings
from aptusadmin.decorators import valid_session


@login_required
@valid_session
def google_api_auth(request):

	from google_auth_oauthlib import flow
	from aptusadmin.oauth.google_api_oauth_helpers import get_google_creds

	creds = get_google_creds(request.user, is_admin=True)
	customuser = request.user
	if not customuser.google_account:
		messages.add_message(
			request, messages.INFO, "Opération impossible, veuillez d'abord spécifier votre compte google.",
			extra_tags='alert-danger'
		)
		return redirect(reverse('aptusadmin:api'))
	
	if creds is None:
		auth_flow = flow.Flow.from_client_secrets_file(
			aptusadmin_settings.GOOGLE_API_CLIENT_SECRETS_FILE,
			scopes=aptusadmin_settings.GOOGLE_API_ADMIN_SCOPES
		)
		auth_flow.redirect_uri = aptusadmin_settings.GOOGLE_API_REDIRECT_URIS[1]
		authorization_url, state = auth_flow.authorization_url(
			access_type='offline',
			login_hint=customuser.google_account,
			include_granted_scopes='true'
		)
		request.session['state'] = state
		return HttpResponseRedirect(authorization_url)
	else:
		messages.add_message(
			request, messages.INFO, f"{aptusadmin_settings.NOM_SOLUTION} a déjà l'accès à cette API.",
			extra_tags='alert-success'
		)
		return redirect(reverse('aptusadmin:api'))


@login_required
@valid_session
def google_api_callback(request):

	from google_auth_oauthlib import flow
	from aptusadmin.oauth.google_api_oauth_helpers import set_google_creds

	state = request.session.get('state')
	error = request.GET.get('error')
	if error:
		messages.add_message(
			request, messages.INFO, f"Opération impossible, {error}.", extra_tags='alert-danger'
		)
		return redirect(reverse('aptusadmin:api'))

	auth_flow = flow.Flow.from_client_secrets_file(
		aptusadmin_settings.GOOGLE_API_CLIENT_SECRETS_FILE, scopes=aptusadmin_settings.GOOGLE_API_ADMIN_SCOPES, state=state
	)
	auth_flow.redirect_uri = aptusadmin_settings.GOOGLE_API_REDIRECT_URIS[1]
	authorization_response = request.build_absolute_uri()
	auth_flow.fetch_token(authorization_response=authorization_response)

	creds = auth_flow.credentials
	set_google_creds(request.user, creds, is_admin=True)
	
	messages.add_message(
		request, messages.INFO,
		"Accès accordé avec succès.", extra_tags='alert-success'
	)
	return redirect(reverse('aptusadmin:api'))
