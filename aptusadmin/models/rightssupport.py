from django.db import models

class RightsSupport(models.Model):
    class Meta:
        managed = False  # No database table creation or deletion  \
                         # operations will be performed for this model. 
        default_permissions = ()
        permissions = ( 
            ('access_to_admin_console', "Accéder à la console d'administration"),  
        )