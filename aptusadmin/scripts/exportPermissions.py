# -*- coding: utf-8 -*-
# scripts/myscript.py
# Usage : python exportPermissions.py [csv]
import sys
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "aptusparc.settings"
import django
django.setup()

from immo.models import *
from django.contrib.auth.models import Permission,Group
from django.core.exceptions import ObjectDoesNotExist
import xlsxwriter

def get_permission(id_groupe,id_permission):
    bool = 'OUI'
    try : 
        Permission.objects.get(pk=id_permission,group__id=id_groupe)
        
    except ObjectDoesNotExist : 
        bool = '-'
    return bool
    
queryset = Permission.objects.exclude(content_type__app_label='admin').exclude(content_type__app_label='contenttypes').\
exclude(content_type__app_label='sessions').exclude(content_type__app_label='auth',content_type__model = 'permission').exclude(content_type__app_label='auth',content_type__model = 'group')
if 'csv' in sys.argv :
    writer = csv.writer(open(settings.BASE_DIR+'/aptusadmin/permissions/Permissions.csv', 'w', newline='', encoding='utf-8'), delimiter=';')
    row = ["Application", "Model", "Code name" ,"Permissions"] 
    for elt in Group.objects.all(): 
        row.append(elt)
    writer.writerow(row)
    for elt in queryset:
        row = [elt.content_type.app_label, elt.content_type.model, elt.codename, elt.name]
        for gr in Group.objects.all(): 
            row.append(get_permission(gr.id,elt.id))        
        writer.writerow(row)
else :
    row = 1
    col = 4 
    workbook = xlsxwriter.Workbook(settings.BASE_DIR+'/aptusadmin/permissions/Permissions.xlsx')
    worksheet = workbook.add_worksheet()
    format1 = workbook.add_format({'border': True}) 
    worksheet.write(0, 0, 'Application',format1); worksheet.write(0, 1, 'Model',format1); worksheet.write(0, 2, 'Code name',format1); worksheet.write(0, 3, 'Permissions',format1) 
    for elt in Group.objects.all():                    
        worksheet.write(0, col, str(elt),format1)
        col += 1
    worksheet.autofilter(0,0,0,col-1)
    for elt in queryset: 
        col = 4
        worksheet.write(row, 0, elt.content_type.app_label,format1); worksheet.write(row, 1, elt.content_type.model, format1); worksheet.write(row, 2, elt.codename, format1); worksheet.write(row, 3, elt.name, format1)    
        for gr in Group.objects.all():
            worksheet.write(row, col, get_permission(gr.id,elt.id),format1)
            col += 1
        row += 1     
    workbook.close()
