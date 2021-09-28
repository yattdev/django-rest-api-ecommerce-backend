# -*- coding: utf-8 -*-
# python DeleteAllPermissions.py
import django
django.setup()

from django.contrib.auth.models import Permission,Group,User
from django.core.exceptions import ObjectDoesNotExist


print("Warnning: Cette action supprimera toutes les permissions de la base de données. pensez à faire un exportPermissions avant de continuer.")
print("Voulez-vous continuer Oui|Non ?")

reponse = input().upper()
if reponse == 'OUI':
    for group in Group.objects.all():
        group.permissions.all().delete()
    for user in User.objects.all():
        user.user_permissions.all().delete()
    Permission.objects.all().delete()    
    print("Suppresion terminée")
else :
    print("Opération non effectuée")
    
