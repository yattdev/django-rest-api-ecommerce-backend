from django.urls import reverse
from rest_framework import serializers
from .models import (Categorie, FichierProduit, ImageSlider, Produit, Client,
                     ProduitPanier, ProduitCommande, Panier, Commande,
                     NoteDeRecommandation, Contact, SiteSettings)
from aptusadmin.models import CustomUser


# Return categorie with enfants
class CategorieSerializer(serializers.ModelSerializer):
    enfants = serializers.SerializerMethodField()

    class Meta:
        depth = 1
        model = Categorie
        fields = ("id", "libelle", "enfants", "view_count", "image")

    def get_enfants(self, obj):
        return CategorieSerializer(obj.get_children(), many=True).data


# Return Categorie with parent
class CategorieSerializer2(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Categorie
        fields = ("id", "libelle", "parent")

    def get_parent(self, obj):
        if obj.parent is not None: return CategorieSerializer2(obj.parent).data
        else: return None


class FichierProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = FichierProduit
        fields = "__all__"


class AjouterProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = "__all__"


class ProduitSerializer2(serializers.ModelSerializer):
    categorie = CategorieSerializer2(read_only=True)
    fichierproduit_set = FichierProduitSerializer(read_only=True, many=True)

    class Meta:
        model = Produit
        fields = ("id", "nom_produit", "prix_produit", "categorie",
                  "fichierproduit_set", "nouveau", "qte_stock")


class ProduitSerializer(serializers.ModelSerializer):
    categorie = CategorieSerializer2(read_only=True)
    fichierproduit_set = FichierProduitSerializer(read_only=True, many=True)
    upsales = ProduitSerializer2(many=True)
    cross_sales = serializers.SerializerMethodField()
    absolute_url = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    note_recommandation = serializers.SerializerMethodField()

    class Meta:
        model = Produit
        fields = "__all__"

    def get_thumbnail(self, obj):
        return obj.get_thumbnail()

    def get_absolute_url(self, obj):
        return reverse('produit_detail', args=(obj.pk, ))

    def get_cross_sales(self, obj):
        cross_sells = Produit.objects.filter(crosssell_set__produit=obj)

        return ProduitSerializer2(cross_sells, many=True).data

    def get_note_recommandation(self, obj):
        return obj.get_note_recommandation()


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "first_name", "last_name", "username", "email")


class ProduitPanierSerializer2(serializers.ModelSerializer):
    class Meta:
        model = ProduitPanier
        fields = "__all__"


class ProduitPanierSerializer(serializers.ModelSerializer):
    id_produit_panier = serializers.ReadOnlyField(source='id')
    id_produit = serializers.ReadOnlyField(source='produit.id')
    nom_produit = serializers.ReadOnlyField(source='produit.nom_produit')
    # image_produit = serializers.ReadOnlyField(source='produit.image.url')
    prix_produit = serializers.ReadOnlyField(source='produit.prix_produit')
    qte_stock_produit = serializers.ReadOnlyField(source='produit.qte_stock')
    qte_produit_panier = serializers.ReadOnlyField(source='qte')

    class Meta:
        model = ProduitPanier
        fields = (
            "id_produit_panier",
            "id_produit",
            "nom_produit",
            "qte_produit_panier",
            "prix_produit",
            "qte_stock_produit",
            # "image_produit",
        )


class ProduitPanierSerializer2(serializers.ModelSerializer):
    class Meta:
        model = ProduitPanier
        fields = ("panier", "produit", "qte")


class PanierSerializer2(serializers.ModelSerializer):
    total = serializers.DecimalField(read_only=True,
                                     max_digits=8,
                                     decimal_places=2)
    produits = ProduitPanierSerializer(source='produitpanier_set', many=True)

    class Meta:
        model = Panier
        fields = ("id", "total", "produits")


class PanierSerializer3(serializers.ModelSerializer):
    total = serializers.DecimalField(read_only=True,
                                     max_digits=8,
                                     decimal_places=2)

    class Meta:
        model = Panier
        fields = ("id", "total", "client")


class ClientSerializer(serializers.ModelSerializer):
    panier = PanierSerializer2(read_only=True)
    password = serializers.CharField(write_only=True)
    # num_cart = serializers.CharField()
    # code_sec = serializers.CharField()
    # date_expiration = serializers.CharField()
    # num_cart = serializers.SerializerMethodField()
    # code_sec = serializers.SerializerMethodField()
    # date_expiration = serializers.SerializerMethodField()
    class Meta:
        model = Client
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "avatar",
            "adresse_livraison",
            "genre",
            "adresse",
            "panier",
            "tel",
            "password",
            # "num_cart", "code_sec", "date_expiration"
        )

    # def get_num_cart(self, obj):
    #     number = ""
    #     for i in range(0, len(obj.num_cart)):
    #         if 12 >= i >= 7: number += "*"
    #         else: number += obj.num_cart[i]
    #     return number

    # def get_date_expiration(self, obj):
    #     return str(obj.date_expiration)

    # def get_code_sec(self, obj):
    #     number = ""
    #     for i in range(0, len(obj.code_sec)):
    #         if i < 2: number += "*"
    #         else: number += obj.code_sec[i]
    #     return number

    def create(self, validated_data):

        user = Client.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
        )

        return user


class PanierSerializer(serializers.ModelSerializer):
    total = serializers.DecimalField(read_only=True,
                                     max_digits=8,
                                     decimal_places=2)
    client = ClientSerializer()
    produits = ProduitPanierSerializer(source='produitpanier_set', many=True)

    class Meta:
        model = Panier
        fields = "__all__"


class ProduitCommmandeSerializer2(serializers.ModelSerializer):
    class Meta:
        model = ProduitCommande
        fields = "__all__"


class ProduitCommmandeSerializer(serializers.ModelSerializer):
    id_produit_commande = serializers.ReadOnlyField(source='id')
    id_produit = serializers.ReadOnlyField(source='produit.id')
    nom_produit = serializers.ReadOnlyField(source='produit.nom_produit')
    image_produit = serializers.ReadOnlyField(source='produit.image.url')
    prix_produit = serializers.ReadOnlyField(source='produit.prix_produit')
    qte_produit_commande = serializers.ReadOnlyField(source='qte')

    class Meta:
        model = ProduitCommande
        fields = ("id_produit_commande", "id_produit", "nom_produit",
                  "qte_produit_commande", "image_produit", "prix_produit")


class CommandeSerializer(serializers.ModelSerializer):
    total = serializers.DecimalField(read_only=True,
                                     max_digits=8,
                                     decimal_places=2)
    client = ClientSerializer()
    produits = ProduitCommmandeSerializer(source='produitcommande_set',
                                          many=True)

    class Meta:
        model = Commande
        fields = "__all__"


class CommandeSerializer2(serializers.ModelSerializer):
    total = serializers.DecimalField(read_only=True,
                                     max_digits=8,
                                     decimal_places=2)

    class Meta:
        model = Commande
        fields = "__all__"


class NoteSerializer(serializers.ModelSerializer):
    client = ClientSerializer()

    # produit_commente = ProduitSerializer()
    class Meta:
        model = NoteDeRecommandation
        fields = "__all__"


class NoteSerializer2(serializers.ModelSerializer):
    class Meta:
        model = NoteDeRecommandation
        fields = "__all__"


# class ClientSerializer(serializers.ModelSerializer):
#     panier = PanierSerializer2(read_only=True)
#     class Meta:
#         model = Client
#         fields = (
#             'id', 'first_name', 'last_name', 'username',
#             'email', 'genre', 'adresse', 'panier'
#         )


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"

    def create(self, validated_data):
        contact = super().create(validated_data)
        contact.send_email()

        return contact


class ImageSliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageSlider
        fields = "__all__"


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = "__all__"
