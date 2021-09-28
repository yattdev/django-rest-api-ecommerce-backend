from django.core.validators import EMPTY_VALUES
from django import forms
from .models import SiteSettings

class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = "__all__"

    def clean(self):
        modes_paiement = self.cleaned_data.get('modes_paiement', False)
        if "V" in modes_paiement:
            banque = self.cleaned_data.get('banque', None)
            rib = self.cleaned_data.get('num_rib', None)
            if banque in EMPTY_VALUES:
                self._errors['banque'] = self.error_class(['Le nom de la banque est obligatoire si vous sélectionnez le mode de paiement par virement!'])
            if rib in EMPTY_VALUES:
                self._errors['num_rib'] = self.error_class(['Le numéro RIB du compte est obligatoire si vous sélectionnez le mode de paiement par virement!'])
        if "P" in modes_paiement:
            paypal_client_id = self.cleaned_data.get('paypal_client_id', None)
            if paypal_client_id in EMPTY_VALUES:
                self._errors['paypal_client_id'] = self.error_class(['Le Client ID du compte Paypal est obligatoire si vous sélectionnez le mode de paiement Paypal!'])
        return self.cleaned_data
