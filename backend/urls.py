"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('e_commerce.urls')),
    path('aptusadmin/', include('aptusadmin.urls')),
    # url(r'^auth/', include('djoser.urls.jwt')),
    url(r'^auth/', include('djoser.urls')),
    url(r'^auth/', include('djoser.urls.authtoken')),
    #  Authentication with rest_framework
    path('auth/rest-auth/', include('rest_framework.urls')), # new
    #  Authentication with dj-rest-framework
    #  path('auth/dj-rest-auth/', include('dj_rest_auth.urls')), # new
    #  Registration with dj-rest-framework
    path('auth/signup',
         include('dj_rest_auth.registration.urls')), # new
    path('i18n/', include('django.conf.urls.i18n')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Add these urls configuration if DEBUG=TRUE
if settings.DEBUG:
    #  import debug_toolbar
    urlpatterns = [
        #  path('__debug__/', include(debug_toolbar.urls)),
    ] +  urlpatterns + static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
