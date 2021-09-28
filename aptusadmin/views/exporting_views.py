# -*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, redirect
from django.contrib.auth.decorators import login_required,permission_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Q
import xlwt
from aptusadmin.models.main_models import *
from aptusadmin.resources import CustomUserResource
from aptusadmin.settings import INSTALLED_APTUS_APPS
from aptusadmin.permissions import export_permission

@login_required
def groupe_exporter_data(request, **kwargs):
    if not export_permission(request.user):
        raise PermissionDenied   
    V = Q()
    for elt in INSTALLED_APTUS_APPS:
        V = V | Q(content_type__app_label=elt)    
    
    def has_permission(groupe, permission):
        bool = 'V'
        try : 
            Permission.objects.get(pk=permission.id, group=groupe)
        except ObjectDoesNotExist : 
            bool = ''
        return bool

    response = HttpResponse(content_type='application/ms-excel')
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Permissions')
    
    if kwargs['target'] == 'export-permissions':
        """ Permet d'exporter les permissions d'un ou plusieurs groupes"""
        response['Content-Disposition'] = 'attachment; filename="aptusapplipermissions.xls"'

        # Sheet header, first row

        entete_style = xlwt.XFStyle()
        entete_style.font.bold = True

        columns = ['CODE PERMISSION', 'PERMISSION']
        if 'groupe_id' in kwargs:
            groupes = CustomGroup.objects.filter(id=kwargs['groupe_id'])
        else: 
            groupes = CustomGroup.objects.all()
        for groupe in groupes:
            columns.append(groupe.name)
        for col_num in range(len(columns)):
            ws.write(0, col_num, columns[col_num], entete_style)
        queryset = CustomPermission.objects.filter(V)

        r = 1
        for permission in queryset:
            columns = [permission.content_type.app_label+'|'+permission.content_type.model+'|'+permission.codename, str(permission), ]
            for groupe in groupes:
                columns.append(has_permission(groupe, permission))
            for c in range(len(columns)):
                ws.write(r, c, columns[c])
            r += 1
        
        wb.save(response)
        return response
        
     
@login_required
def export_data(request, **kwargs):
    if kwargs['target'] == 'pwdenseignants':
        my_resource = CustomUserResource()
        qset = CustomUser.objects.filter(groups=Group.objects.get(name='ENSEIGNANT'), must_change_pwd=True)
        dataset = my_resource.export(qset)
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="ensignants.xls"'
        return response

    
