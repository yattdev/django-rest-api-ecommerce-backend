# -*- coding: utf-8 -*-
# python createbackup.py
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "aptusparc.settings"
import django
django.setup()

from myapps.models import Backup


print("Start Backup ...")

backup = Backup(creation_mode='SCHEDULED')
backup.c_create(with_mess=False)
print("End Backup.")    