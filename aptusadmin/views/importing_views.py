# -*- coding: utf-8 -*-
import xlrd
from django.shortcuts import render, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib import messages
from django.contrib.auth.models import Permission
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from aptusadmin.templatetags.aptusadmin_filter import get_dirname
from aptusadmin.models.main_models import CustomGroup
from aptusadmin.permissions import  import_permission
from aptusadmin.utils import handle_excel_file, handle_uploaded_file
from aptusadmin.settings import TMP_DIR, list_path_template, view_path_template, form_path_template
from aptusadmin.forms import GenericImportForm


@login_required
def groupe_importer_data(request, **kwargs):
    if not import_permission(request.user):
        raise PermissionDenied   
    if kwargs['target'] == 'import-permissions':
        """ """
        notfound_permissions = []
        if request.method == 'POST':            
            if( request.POST.__getitem__('action') == 'envoyer'):
                try:
                    f = handle_uploaded_file(request.user, request.FILES['xlfile'])
                    wb = xlrd.open_workbook(f)
                    sh = wb.sheet_by_index(0)
                    entete = sh.row_values(0)
                    list_group =  entete[2:]                       
                    for rownum in range(1,sh.nrows):
                        row = sh.row_values(rownum)
                        code_permission = row[0].split('|') 
                        try:
                            permission = Permission.objects.get(content_type__app_label=code_permission[0], content_type__model=code_permission[1], codename=code_permission[2])
                            for i in range(len(row[2:])):
                                group, c = CustomGroup.objects.get_or_create(name=list_group[i].upper())
                                if row[2:][i].upper() == 'V':
                                    group.permissions.add(permission)
                                else: 
                                    group.permissions.remove(permission)
                        except ObjectDoesNotExist:
                            notfound_permissions.append(row[0])
                    #### Fin du traitement du fichier  ####
                    message = ('success',"l'import a été effectué avec succès. </br> les permission suivantes n'exitent pas dans la base:" + str(notfound_permissions))
                except Exception as e: 
                    message = ('danger', "L'outil d'import a rencontré une anomalie à la ligne "+ str(rownum+1) +". Merci de corriger et reprendre l'import. <br>" + str(e))
                messages.add_message(request, messages.INFO, message[1], extra_tags='alert-'+message[0])
                return HttpResponseRedirect(get_dirname(request.get_full_path()))        
        context = {
                   'active_groupes':True,
                    'dirname_str':'Permissions',
                   }
        return render(request, 'aptusadmin/main/import_etape1.html', context)


@login_required
def generic_import(request, redirect_url, parent_template, cls, step_1_template='', step_2_template='', excel_template_filename=None, fields_to_import_infos={}, import_infos={}, header_row=0):

    if not hasattr(cls, 'get_import_form_fields') or not hasattr(cls, 'import_objects'):
        raise Http404
    
    step_2_template = 'aptusadmin/import/etape2.html' if not step_2_template else step_2_template
    step_1_template = 'aptusadmin/import/etape1.html' if not step_1_template else step_1_template
    
    if request.method == 'POST':
        if request.POST.get('action') == 'envoyer':
            f = handle_uploaded_file(request.user, request.FILES['xlfile'])
            rows = handle_excel_file(f, header_row)
            form_fields = cls.get_import_form_fields(**fields_to_import_infos)
            form = GenericImportForm(
                cls=cls, fields=form_fields, entete=rows[header_row], initial={'path': f}
            )
            context = {
                'rows':rows,
                'form':form,
                'parent_template': parent_template,
                'cls': cls,
                'excel_template_filename': excel_template_filename,
                'redirect_url': redirect_url,
            }
            return render(request, step_2_template, context)    

        if request.POST.get('action') == 'enregistrer':
            rows = handle_excel_file(request.POST.get("path"), header_row)

            form_fields = cls.get_import_form_fields(**fields_to_import_infos)
            form = GenericImportForm(
                cls=cls, fields=form_fields, entete=rows[header_row], data=request.POST
            )

            if form.is_valid():
                message = form.importer(form.cleaned_data['path'], **import_infos) 
                messages.add_message(request, messages.INFO, message[1], extra_tags='alert-'+message[0])
                return HttpResponseRedirect(redirect_url)
                
            else:
                context = {
                    'rows':rows,
                    'form':form,
                    'parent_template': parent_template,
                    'cls': cls,
                    'excel_template_filename': excel_template_filename,
                    'redirect_url': redirect_url,
                }
                return render(request, step_2_template,context) 
    
    context = {
        'redirect_url': redirect_url,
        'parent_template': parent_template,
        'cls': cls,
        'excel_template_filename': excel_template_filename,
    }
    return render(request, step_1_template, context)
