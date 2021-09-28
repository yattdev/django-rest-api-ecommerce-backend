# -*- coding: utf-8 -*-
# python importPermission.py
import sys
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "aptusparc.settings"
import django
django.setup()
from immo.models import *
from django.contrib.auth.models import Permission,Group
from django.core.exceptions import ObjectDoesNotExist

reader = csv.reader(open(settings.BASE_DIR+'/aptusadmin/permissions/importPermissions.csv', encoding='utf-8'), delimiter=';')
list_group =  next(reader)[4:]  
for row in reader:
    try:
        permission = Permission.objects.get(content_type__app_label=row[0], content_type__model=row[1], codename=row[2])
    except ObjectDoesNotExist:
        print(row[0], row[1], row[2], "n'existe plus dans la base")
    for i in range(len(row[4:])):
        group, c = Group.objects.get_or_create(name=list_group[i])
        if row[4:][i] == 'OUI':
            group.permissions.add(permission)
        elif row[4:][i] == '-': 
            group.permissions.remove(permission)
print("Fin d'import")
            