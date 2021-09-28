# -*- coding: utf-8 -*-
from datetime import datetime
import os
from io import StringIO, BytesIO
from django.contrib.auth.models import UserManager
from slugify import slugify

import xlrd

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from xhtml2pdf import pisa

from django.db import models
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template

from aptusadmin import settings as myapps_settings


class MyappsManager(models.Manager):
    def get_prev_and_next_items(self,target, items): #pagination par élément
        found = False
        prev = None
        next = None
        num=-1
        for item in items:
            num+=1
            if found:
                next = item
                break
            if item.pk == target.pk:
                found = True
                continue
            prev = item
        return (prev, next,num,items.count())
    
    def get_all_children(self,instance):
        r = ()
        queryset = self.model.objects.filter(parent=instance)
        if queryset.count()>0:
            list=[]
            r += ((instance.id,instance.nom),)
            for elt in queryset:
                obj = self.get_all_children(elt)
                
                if 0 < len(obj):
                    list.append(obj)
            r += (list,)        
        else:
            r += ((instance.id,instance.nom))    
        return r
    
    def all_hierarchical(self):
        list=[('','----------')]
        for elt in self.model.objects.filter(parent=None):
            list.append(self.get_all_children(elt))
        return list


class CustomUserManager(MyappsManager, UserManager):
    pass


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.drawRightString(40*mm, 3*mm,
            datetime.now().strftime('%d/%m/%Y %H:%M') )
        self.drawRightString(280*mm, 3*mm,
            "Page %d / %d" % (self._pageNumber, page_count))


def handle_uploaded_file(user, f, target_dir=myapps_settings.TMP_DIR):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    prefix = slugify(user.first_name+'-'+user.last_name)
    file_name = prefix+'-'+datetime.now().strftime("%y%m%d-%H%M%S")+'-'+str(f).replace(' ','_')
    file_path = os.path.join(target_dir, file_name)
    target_file = open(file_path, 'wb+')
    for chunk in f.chunks():
        target_file.write(chunk)
    target_file.close()
    return file_path


def handle_excel_file(f, line_number=0):
    wb = xlrd.open_workbook(f)
    sh = wb.sheet_by_index(0)
    nbr_rows = 4 + line_number if sh.nrows >= 4 + line_number else sh.nrows
    rows = [sh.row_values(0)] 
    nbr_column = len(sh.row_values(0))
    for rownum in range(1, nbr_rows):
        rows.append(sh.row_values(rownum)[0:nbr_column])
    return rows 


def can_backup_restore():
    if os.path.exists(os.path.join(settings.BACKUP_ROOT, 'backup_flag')) or os.path.exists(os.path.join(settings.BACKUP_ROOT, 'restore_flag')):
        bool = False
    else:
        bool = True    
    return bool


def str_to_bool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False
    elif s == 'None':
        return None
    else:
        raise ValueError # evil ValueError that doesn't tell you what the wrong value was


def render_to_pdf(template_src, context_dict={}):
    
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(StringIO(html), result, encoding='UTF-8')
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def write_pdf(template_src, context_dict, filename):
    template = get_template(template_src)
    html  = template.render(context_dict)
    file = open(filename, 'wb') # Changed from file to filename
    pisaStatus = pisa.CreatePDF(html.encode("utf-8"), dest=file, encoding='utf-8')


def password_generator(size=8):
    import random
    chars = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
    pwd = "".join(random.sample(chars, size))
    return pwd


def username_generator(size=8):
    import random
    chars = "123456789"
    username = "".join(random.sample(chars, size))
    return username


def log_action(logfile, message):
    logfile.write(f"'{datetime.now().strftime('%d/%m/%Y %H:%M')}': {message}.\n")
    return True
