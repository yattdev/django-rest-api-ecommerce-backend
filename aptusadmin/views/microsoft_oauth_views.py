from django.http import HttpResponseRedirect
from django.shortcuts import redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from aptusadmin.oauth.microsoft_oauth_helpers import get_sign_in_flow, get_token_from_code

from aptusadmin.decorators import valid_session


@login_required
@valid_session
def microsoft_api_auth(request):
	customuser = request.user
	if not customuser.microsoft_account:
		messages.add_message(
			request, messages.INFO,
			"Opération impossible, veuillez d'abord spécifier votre compte microsoft.",
			extra_tags='alert-danger'
		)
		return redirect(reverse('aptusadmin:api'))

	flow = get_sign_in_flow()

	try:
		request.session['auth_flow'] = flow
	except Exception as e:
		messages.add_message(request, messages.INFO, str(e), extra_tags='alert-danger')

	return HttpResponseRedirect(flow['auth_uri'])


@login_required
@valid_session
def microsoft_api_callback(request):
	result = get_token_from_code(request)
	if result.get('error'):
		messages.add_message(
			request, messages.INFO, result['error_description'],
			extra_tags='alert-danger'
		)
		return HttpResponseRedirect(reverse('aptusadmin:api'))

	messages.add_message(
		request, messages.INFO,
		"Accès accordé avec succès.", extra_tags='alert-success'
	)
	return HttpResponseRedirect(reverse('aptusadmin:api'))

