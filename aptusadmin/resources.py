from import_export import resources
from aptusadmin.models import CustomUser

class CustomUserResource(resources.ModelResource):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'tmp_pwd', )
        export_order = ('first_name', 'last_name', 'username', 'tmp_pwd')
