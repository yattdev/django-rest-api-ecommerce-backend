from django.conf.urls import url
from . import views

app_name = 'aptusadmin'

urlpatterns = [
    url(r'^$', views.myappslist, name='myappslist'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate/(?P<uid>[\w-]+)/(?P<token>[\w-]+)/$', views.activate, name="activate"),
    url(r'^password_reset/(?P<uid>[\w-]+)/(?P<token>[\w-]+)/$', views.password_reset, name="password_reset"),
    url(r'^password_reset_confirm/$', views.password_reset_confirm, name="password_reset_confoirm"),
    url(r'^connexion/$', views.connexion, name='connexion'),
    url(r'^deconnexion$', views.deconnexion, name='deconnexion'),
    url(r'^admin/$', views.admin_home, name='admin_home'),
    url(r'^backuprestore/$', views.backup_restore, name='backup_restore'),
    url(r'^changepassword/$', views.change_password, name='change_password'),
    # ##############################################################################
    
    url(r'^set_screen_size/$', views.set_screen_size, name='set_screen_size'),
    url(r'^exportdata/(?P<target>\w+)/$', views.export_data, name='export_data'),

    # ######### utilisateurs #######################################################
    url(r'^utilisateur/$', views.utilisateurs, name='utilisateurs'),
    url(r'^utilisateur/(?P<utilisateur_id>[0-9]+)/$', views.utilisateur_consulter, name='utilisateur_consulter'),
    url(r'^utilisateur/add/$', views.utilisateur_creer, name='utilisateur_creer'),
    url(r'^utilisateur/(?P<utilisateur_id>[0-9]+)/update/$', views.utilisateur_modifier, name='utilisateur_modifier'),
    url(r'^utilisateur/back-to-original-profile/$', views.back_to_original_profile, name='back_to_original_profile'),
    
    # ######### groupes #######################################################
    url(r'^groupe/$', views.groupes, name='groupes'),
    url(r'^groupe/(?P<groupe_id>[0-9]+)/$', views.groupe_consulter, name='groupe_consulter'),
    url(r'^groupe/add/$', views.groupe_creer, name='groupe_creer'),
    url(r'^groupe/(?P<target>export-\w+)/$', views.groupe_exporter_data, name='groupe_exporter_data'),
    url(r'^groupe/(?P<target>import-\w+)/$', views.groupe_importer_data, name='groupe_importer_data'),
    url(r'^groupe/(?P<groupe_id>[0-9]+)/update/$', views.groupe_modifier, name='groupe_modifier'),
    url(r'^groupe/(?P<groupe_id>[0-9]+)/(?P<target>export-\w+)/$', views.groupe_exporter_data, name='groupe_exporter_data'),

    # ######### APIs #######################################################
    url(r'^api/$', views.api_list, name='api'),
    # Google
    url(r'^google-api/auth/$',views.google_api_auth, name='google_api_auth'),
    url(r'^google-api/callback/$',views.google_api_callback, name='google_api_callback'),
    # Microsoft
    url(r'^microsoft-api/auth/$',views.microsoft_api_auth, name='microsoft_api_auth'),
    url(r'^microsoft-api/callback/$',views.microsoft_api_callback, name='microsoft_api_callback'),

    # ######### messages #######################################################
    url(r'^message/$', views.messages_liste, name='messages'),
    url(r'^message/([0-9]+)/$', views.message_consulter, name='message_consulter'),
    url(r'^get_message/$', views.get_message, name='get_message'),
    url(r'^get_nbr_message/$', views.get_nbr_message, name='get_nbr_message'),

    # ######### logentry #######################################################
    url(r'^logentry/$', views.logentry_liste, name='logentry_liste'),
    url(r'^alert/$', views.alert_liste, name='alert_liste'),

    # ######### EMAIL VALIDATION URLS ##########################################
    url(r'^validate/$', views.send_validation_link, name='send_validation_link'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<mailb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/(?P<tcdb64>[0-9A-Za-z_\-]+)/$',
        views.activate_mail_adress, name='activate_mail_adress'),

    # ######### PASSWORD RESET URLS ##########################################
    url(r'^reset_password1/$', views.send_password_reset_link, name='send_password_reset_link'),
    url(r'^reset_password2/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/(?P<tcdb64>[0-9A-Za-z_\-]+)/$',
        views.reset_password, name='reset_password'),
]
