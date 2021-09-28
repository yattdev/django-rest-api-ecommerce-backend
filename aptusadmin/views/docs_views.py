import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.contrib.auth.decorators import login_required


@login_required
def docs_server(request, filename):
    
    template_name = filename.split('-')[1] + '/docs/' + filename

    return render(request, template_name)
