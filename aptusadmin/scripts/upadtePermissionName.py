# -*- coding: utf-8 -*-
# scripts/upadtePermissionName.py
# Usage : python upadtePermissionName.py [export|import]
import os
import sys
os.environ["DJANGO_SETTINGS_MODULE"] = "aptusparc.settings"
import django
django.setup()

from immo.models import *
from django.contrib.auth.models import Permission,Group
from django.core.exceptions import ObjectDoesNotExist


if len(sys.argv) == 2 :
    if 'export' in sys.argv :
        writer = csv.writer(open(settings.BASE_DIR+'/aptusadmin/permissions/exportPermissionsName.csv', 'w', newline='', encoding='utf-8'), delimiter=';')
        writer.writerow(["Application", "Model", "Code name" ,"Permissions"])
        for elt in Permission.objects.exclude(content_type__app_label='admin').exclude(content_type__app_label='contenttypes').\
        exclude(content_type__app_label='sessions').exclude(content_type__app_label='auth',content_type__model = 'permission').exclude(content_type__app_label='auth',content_type__model = 'group'):
            writer.writerow([elt.content_type.app_label, elt.content_type.model, elt.codename, elt.name])
        print("Fin d'export")
    
    elif 'import' in sys.argv :
        reader = csv.reader(open(settings.BASE_DIR+'/aptusadmin/permissions/importPermissionsName.csv', encoding='utf-8'), delimiter=';')
        next(reader)
        for row in reader:
            try:
                permission = Permission.objects.get(content_type__app_label=row[0], content_type__model=row[1], codename=row[2])
                permission.name = row[3].strip()
                permission.save()
            except ObjectDoesNotExist:
                print(row[0], row[1], row[2], "n'existe plus dans la base")
        print("Fin d'import")
    else :
        print("Usage : python manage.py upadtePermissionName.py export|import")
else : 
    print("Usage : python manage.py upadtePermissionName.py export|import")