from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

from aptusadmin.models import CustomUser
from aptusadmin.permissions import viewlist_apis
from aptusadmin.decorators import valid_session


@login_required
@valid_session
def api_list(request):

    if not viewlist_apis(request.user):
        raise PermissionDenied
    
    api_list = [
        {
            'icon': 'google_sdk.png',
            'name': 'Google Admin SDK API',
            'function': "Activer la collecte automatique des absences depuis Aptus E-Learn. (Via Google Meet)",
            'is_active': False,
            'link': reverse('aptusadmin:google_api_auth')
        },
        {
            'icon': 'ms_azure.png',
            'name': 'Microsoft Azure API',
            'function': "Activer la collecte automatique des absences depuis Aptus E-Learn. (Via Microsoft Teams)",
            'is_active': False,
            'link': reverse('aptusadmin:microsoft_api_auth')
        },
    ]
    
    context = {
        'api_list': api_list,
        'active_api': True,
    }
    return render(request, 'aptusadmin/api/api-liste.html', context)
