from e_commerce.forms import SiteSettingsForm
from django.contrib import admin
from .models import *
from mptt.admin import DraggableMPTTAdmin
from django.shortcuts import redirect
from backend.settings import FRONT_END
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.db.models.functions import TruncDay

def get_app_list(self, request):
    """
    Return a sorted list of all the installed apps that have been
    registered in this site.
    """
    # Retrieve the original list
    app_dict = self._build_app_dict(request)
    app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower(), reverse=True)

    # Sort the models customably within each app.
    for app in app_list:
        if app['app_label'] == 'e_commerce':
            ordering = {
                'Produits': 1,
                'Categories': 2,
                'Clients': 3,
                'Commandes': 4,
                'Paniers': 5,
                'Notes de recommandation': 6,
                'Contacts': 7,
                'Paramètres du site': 8,
            }
            app['models'].sort(key=lambda x: ordering[x['name']])

    return app_list

admin.AdminSite.get_app_list = get_app_list

admin.site.site_header = "Site d'administration e-commerce"
admin.site.site_url = FRONT_END

@admin.register(Categorie)
class CategorieAdmin(DraggableMPTTAdmin):
    list_display = ("id", "tree_actions", "indented_title", "view_count", "nb_produits")
    search_fields = ("libelle", )
    list_editable = ("view_count", )

    def changelist_view(self, request, extra_context=None):
        chart_data = (
            Categorie.objects.all().values("libelle")
        )

        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {"chart_data": as_json}

        return super().changelist_view(request, extra_context=extra_context)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("image", "email", "first_name", "last_name", "tel", "genre", "is_active")
    list_display_links = ("email", )
    list_filter = ("is_active", "genre")
    search_fields = ("email", "first_name", "last_name", "tel", "adresse")
    list_editable = ("is_active", )
    list_per_page = 10
    fieldsets = (
            (None, {
                'fields': (
                    ('first_name', 'last_name'),
                    ('email', 'username'),
                    ('tel', 'genre'),
                    ('adresse', 'adresse_livraison'),
                    ('date_joined', 'avatar'),
                    ('is_active', ),
                )
            }),
        )

class ProduitCommandeInline(admin.TabularInline):
    model = ProduitCommande
    fk_name = "commande"
    extra = 1

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "date_commande", "total", "mode_livraison", "mode_paiement", "payee")
    list_filter = ("payee", "date_commande", "mode_livraison", "mode_paiement")
    search_fields = ("client__username", "client__email", "client__first_name", "client__last_name", "client__adresse_livraison")
    list_editable = ("payee", "mode_livraison", "mode_paiement")
    list_per_page = 10
    fields = [
        ("client", "payee"),
        ("mode_livraison", "mode_paiement"),
    ]
    inlines = [
        ProduitCommandeInline,
    ]

    def changelist_view(self, request, extra_context=None):
        # Aggregate new commandes per day
        chart_data = (
            Commande.objects.annotate(date=TruncDay("date_commande"))
            .values("date")
            .annotate(y=Count("id"))
            .order_by("-date")
        )

        # Serialize and attach the chart data to the template context
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {"chart_data": as_json}

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("id", "fullname", "email", "subject", "message")
    search_fields = ("fullname", "email", "subject", "message")
    list_per_page = 10

@admin.register(NoteDeRecommandation)
class NoteDeRecommandationAdmin(admin.ModelAdmin):
    list_display = ("note", "commentaire", "client", "produit_commente", "date")
    list_filter = ("date", "note")
    search_fields = ("commentaire", "client__username", "client__first_name", "client__last_name", "client__email", "produit_commente__nom_produit")
    list_per_page = 10
    fields = [
        ("client", "produit_commente"),
        "note", "commentaire"
    ]

class ProduitPanierInline(admin.TabularInline):
    model = ProduitPanier
    fk_name = "panier"
    extra = 1

@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "total")
    search_fields = ("client__first_name", "client__last_name", "client__email", "client__username")
    list_per_page = 10
    inlines = [
        ProduitPanierInline,
    ]

class FichierProduitInline(admin.TabularInline):
    model = FichierProduit
    fk_name = "produit"
    extra = 1
    min_num = 1
    verbose_name = "Image du produit"
    verbose_name_plural = "Images du produit"

class CrossSellInline(admin.TabularInline):
    model = CrossSell
    fk_name = "produit"
    extra = 1
    verbose_name_plural = "Cross sells: Ce champ est utilisé pour trier les produits par popularité."

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ("image", "nom_produit", "prix_produit", "categorie", "qte_stock", "date_ajout", "view_count", "get_note_recommandation", "nouveau")
    readonly_fields = ('image', )
    list_display_links = ("nom_produit", )
    list_filter = ("date_ajout", "categorie", "nouveau")
    search_fields = ("nom_produit", "categorie__libelle")
    filter_horizontal = ('upsales', 'cross_sales')
    list_editable = ("qte_stock", "view_count", "nouveau")
    list_per_page = 15
    fieldsets = (
            (None, {
                'fields': (
                    ('reference_produit', 'nom_produit'),
                    ('prix_produit', 'categorie'),
                    ("qte_stock", "view_count", "nouveau"),
                    ('description_produit'),
                    ("descriptif", ),
                    ("upsales", ),
                )
            }),
        )
    inlines = [
        FichierProduitInline, CrossSellInline
    ]

    def changelist_view(self, request, extra_context=None):
        chart_data = (
            Produit.objects.annotate(date=TruncDay("date_ajout"))
            .values("date")
            .annotate(y=Count("id"))
            .order_by("-date")
        )

        # Serialize and attach the chart data to the template context
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {"chart_data": as_json}

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)

class ImageSliderInline(admin.TabularInline):
    model = ImageSlider
    fk_name = "site_settings"
    extra = 1
    min_num = 1
    # can_delete = False

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsForm
    list_display = ("nom_entreprise", "site_primary_color", "tel_contact", "adresse", "horaires_travail")
    inlines = [
        ImageSliderInline,
    ]

    def response_change(self, request, obj):
        return redirect('/admin/e_commerce/sitesettings/1/change/')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
