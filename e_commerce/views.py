from e_commerce.models import Produit
#  from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView


class HomeTemplatePage(TemplateView):
    template_name = 'e_commerce/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['liste_produits'] = Produit.objects.all()

        return context


#  def nb_produits():
#  return Produit.objects.all().count()
#
#  def nb_categories():
#  return Categorie.objects.all().count()
#
#  def nb_clients():
#  return Client.objects.all().count()
#
#  def nb_commandes():
#  return Commande.objects.all().count()
#
#  def nb_paniers():
#  return Panier.objects.all().count()
#
#  def nb_notes():
#  return NoteDeRecommandation.objects.all().count()
#
#  def nb_messages():
#  return Contact.objects.all().count()
