from django import forms
from django.forms import widgets


class GenericImportForm(forms.Form):

    def __init__(self, cls, fields, entete, *args, **kwargs):

        self.cls = cls
        
        super(GenericImportForm, self).__init__(*args, **kwargs)
        
        # Prepare choices list
        choices = [("","--------")]
        for i in range(0,len(entete)):
            choices.append((i, entete[i]))
        
        # Create form fields
        for field in fields:
            if isinstance(field, str):  # str: field_name
                field_meta = self.cls._meta.get_field(field)
                field_name = field
                label = field_meta.verbose_name
                required = field_meta.blank
            else:  # tuple: (field_name, label, required)
                field_name, label, required = field
            self.fields[field_name] = forms.ChoiceField(
                label=label,
                choices=choices,
                widget=widgets.Select(attrs={'class': 'form-control'}),
                required=required,
            )
    
    path = forms.CharField(widget = forms.HiddenInput(), required = False)

    def importer(self, path, **kwargs):
        return self.cls.import_objects(cleaned_data=self.cleaned_data, path=path, **kwargs)
