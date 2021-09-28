# -*- coding: utf-8 -*-
import os
import subprocess 
import tarfile
from shutil import rmtree, copy
from threading import Thread
from datetime import datetime
from django.db import models
from aptusadmin.models.main_models import Message, CustomUser
from django.conf import settings
from django.contrib.auth.models import User
from aptusadmin.settings import message_content, message_subject, PG_PATH, ETABLISSEMENT
from aptusadmin.utils import can_backup_restore, handle_uploaded_file

class Backup(models.Model):
    class Meta:
        default_permissions = ('add', 'delete','viewlist')
        verbose_name_plural = "Sauvegardes"
        ordering = ['-creation_date']
    creation_mode_options = (('MANUAL', 'Manuel'), ('SCHEDULED', 'Programmé'), ('IMPORTED', 'Importé'))
    
    creation_mode = models.CharField('Mode de création', max_length=10, choices=creation_mode_options, default="MANUAL")
    creation_date = models.DateTimeField('Date de création')
    file = models.CharField(max_length=50)
    def meta(self):
        return self._meta     
    def get_size(self):
        file = os.path.join(settings.BACKUP_ROOT, self.file)
        if os.path.exists(file):
            var = round(os.stat(file).st_size/1024, 1)
        else:
            var = None    
        return var
        
    def c_create(self, with_mess=True, user=None):
        if not os.path.exists(settings.BACKUP_ROOT):
            os.makedirs(settings.BACKUP_ROOT)
        if can_backup_restore():
            backup_flag = os.path.join(settings.BACKUP_ROOT, 'backup_flag')
            project_name = settings.ROOT_URLCONF.replace('.urls', '')
            etablissement = ETABLISSEMENT['code']
            self.creation_date = datetime.now()
            dump_file = os.path.join(settings.BASE_DIR, f"{etablissement}-{project_name}-database.dump")
            self.file = f"{etablissement}-{project_name}_Backup-{self.creation_date.strftime('%Y-%m-%d-%Hh%M')}.tar.gz"
            tar_file = os.path.join(settings.BACKUP_ROOT, self.file)
            database = settings.DATABASES['default']
            
            obj = self
            class thread_backup (Thread):
                def __init__(self):
                    Thread.__init__(self)
                def run(self):
                    try:
                        open(backup_flag, "w").close()
                        my_env = os.environ
                        my_env["PGPASSWORD"] = database['PASSWORD']
                        my_env["PATH"] = PG_PATH
                        ps = subprocess.Popen(['pg_dump', '-d', database['NAME'], '-h', database['HOST'], '-p', database['PORT'], '-U', database['USER'], '-w', '-f', dump_file], stdout=subprocess.PIPE, env=my_env)
                        output = ps.communicate()[0]
                        
                        def set_info(tarinfo):
                            tarinfo.gname = obj.creation_date.strftime('%Y-%m-%d-%Hh%M')
                            return tarinfo    
                        
                        tar = tarfile.open(tar_file, "w:gz")
                        tar.add(settings.BASE_DIR, arcname=project_name, filter=set_info)
                        tar.close()
                        os.remove(dump_file)
                        obj.save()
                        if with_mess:
                                message=Message()
                                message.date_reception = datetime.now()
                                message.user = user
                                message.sender = CustomUser.objects.get(username='aptusadm')
                                message.subject = message_subject()
                                message.content = message_content(obj.file)
                                message.c_create()                
                        os.remove(backup_flag)
                    except Exception  as e:
                        if with_mess:
                                message=Message()
                                message.date_reception = datetime.now()
                                message.user = user
                                message.sender = CustomUser.objects.get(username='aptusadm')
                                message.subject = "Erreur de sauvegarde."
                                message.content = "La sauvegarde a echoué avec le message: <br>"+str(e)
                                message.c_create()                
                        
                    
            thread_backup = thread_backup()
            thread_backup.start()

            return ("success","La sauvegarde des données va être créée. Vous recevrez un message une fois l'opération terminée.")
        else:
            return ("danger", "Opération impossible, une opération de sauvegarde ou de restaure est en cours.")
    
    def c_delete(self):
        file_path = os.path.join(settings.BACKUP_ROOT, self.file)
        if os.path.exists(file_path):
            os.remove(file_path)
        self.delete()
    def restore(self,pin):
        if can_backup_restore():
            return ('warning',"La retauration de "+ self.file + " ne peut se faire qu'en ligne de commande. Pendant la retauration tous les utilsateurs connectés vont être deconnectés.")
        else:
            return ("danger", "Opération impossible, une opération de sauvegarde ou de restaure est en cours.")
            
