# -*- coding: utf-8 -*-
# python postinstall.py
import os
import django
django.setup()
from myapps.models import CustomUser

""" Create aptusadm user """
 
obj = CustomUser()
obj.username = 'aptusadm'
obj.first_name="Admin Aptus"
obj.is_active = True
obj.is_superuser = True
obj.is_staff = True
res, message = obj.c_create(pwd='changeme')

print ("L'utilsateur", obj.username, "est crée")                                
print("Fin postinstall")
