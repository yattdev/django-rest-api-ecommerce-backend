from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from aptusadmin.models import CustomUser
from django.db.models import Sum
from django.core.mail import send_mail
from django.core.cache import cache
from PIL import Image
from io import BytesIO
from django.core.files import File

from mptt.models import MPTTModel, TreeForeignKey
from ckeditor.fields import RichTextField
from colorfield.fields import ColorField
from multiselectfield import MultiSelectField

CLIENT_GENRE_CHOICES = (("", ""), ('F', 'Femme'), ('H', 'Homme'))


class Client(CustomUser):
    class Meta:
        ordering = []
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        default_permissions = ()

    tel = models.CharField("Téléphone", max_length=25, default="", blank=True)
    genre = models.CharField("Genre",
                             max_length=1,
                             choices=CLIENT_GENRE_CHOICES,
                             default="H",
                             blank=True)
    adresse = models.CharField("Adresse",
                               max_length=128,
                               default="",
                               blank=True)
    adresse_livraison = models.CharField("Adresse de livraison",
                                         max_length=128,
                                         default="",
                                         blank=True)

    # num_cart = models.CharField("Numero de la carte de paiement", max_length=19, blank=True, default="")
    # date_expiration = models.DateField("Date d'expiration de la carte de paiement", blank=True, null=True)
    # code_sec = models.CharField("Code de sécurité de la carte de paiement", max_length=4, blank=True, default="")

    def __str__(self):
        return self.username

    def image(self):
        from django.utils.html import format_html

        if self.avatar:
            return format_html(
                '<img style="object-fit: contain; border-radius: 50%" width=50 height=50 src="http://localhost:8000'
                + self.avatar.url + '"/>')
        else:
            return format_html(
                '<img src="https://www.pngkit.com/png/full/281-2812821_user-account-management-logo-user-icon-png.png" width=50 height=50 />'
            )

    image.short_description = 'Avatar'
    image.allow_tags = True


class Categorie(MPTTModel):
    class Meta:
        verbose_name = 'Categorie'
        verbose_name_plural = 'Categories'
        default_permissions = ()

    libelle = models.CharField(verbose_name="Libellé", max_length=64)
    parent = TreeForeignKey('self',
                            verbose_name="Parent",
                            related_name="Enfants",
                            null=True,
                            blank=True,
                            on_delete=models.CASCADE)
    image = models.ImageField(upload_to='produits/categories/images',
                              blank=True)
    view_count = models.IntegerField(
        default=0,
        verbose_name="Nombre de vues",
        help_text=
        "Ce champ est utilisé pour trier les catégories par popularité.")

    class MPTTMeta:
        order_insertion_by = ['libelle']

    def __str__(self):
        return self.libelle

    def get_children(self):
        return Categorie.objects.filter(parent=self)

    child_categories = []

    def get_family_tree(self, obj):
        if self == obj: self.child_categories = []

        obj.child_categories.append(self)

        children = self.get_children()

        if children:
            for child in children:
                child.get_family_tree(obj)

    def increase_view_count(self):
        v = self.view_count
        v = v + 1
        self.view_count = v
        self.save()

    def nb_produits(self):
        return Produit.objects.filter(categorie=self).count()

    nb_produits.short_description = "Nombre des produits"


class Produit(models.Model):
    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        default_permissions = ()
        ordering = ['-id']

    reference_produit = models.CharField(
        verbose_name="Référence",
        help_text="La référence du produit doit être unique!",
        unique=True,
        max_length=64)
    nom_produit = models.CharField(verbose_name="Nom", max_length=64)
    prix_produit = models.DecimalField(verbose_name="Prix",
                                       max_digits=8,
                                       decimal_places=2,
                                       help_text="Prix du produit en Dhs.")
    description_produit = RichTextField(verbose_name="description")
    descriptif = models.TextField('Descriptif', default="", blank=True)
    categorie = TreeForeignKey(Categorie,
                               verbose_name="Catégorie",
                               on_delete=models.CASCADE)
    qte_stock = models.PositiveIntegerField(verbose_name="Quantité en stock",
                                            null=True,
                                            blank=True)
    upsales = models.ManyToManyField(
        to='self',
        verbose_name="Upsells",
        help_text=
        "Upselling est une pratique qui consiste à encourager les clients à acheter un produit haut de gamme comparable à celui en question.<br/>"
    )
    cross_sales = models.ManyToManyField(
        to='self',
        verbose_name="Cross-sells",
        through="CrossSell",
        blank=True,
        help_text=
        "Cross-selling est une pratique qui invite les clients à acheter des articles liés ou complémentaires à des produits dans leurs paniers.<br/>"
    )
    view_count = models.IntegerField(
        default=0,
        verbose_name="Nombre de vues",
        help_text="Ce champ est utilisé pour trier les produits par popularité."
    )
    date_ajout = models.DateField(auto_now_add=True)
    nouveau = models.BooleanField(
        default=False,
        help_text=
        "Marquer le produit comme 'nouveau', pour l'afficher dans la liste des nouveautés dans la page d'accueil"
    )

    thumbnail = models.ImageField(upload_to="images/products/products_thumb/",
                                  blank=True,
                                  null=True,
                                  )

    def get_thumbnail(self):
        if self.thumbnail:
            return "http://localhost:8000"+self.thumbnail.url
        else:
            fichier_produit = FichierProduit.objects.filter(produit=self)
            if fichier_produit[0].piece_jointe.url:
                return 'http://localhost:8000'+ fichier_produit[0].piece_jointe.url
            return ''

    def __str__(self):
        return self.nom_produit

    def get_note_recommandation(self):
        notes = NoteDeRecommandation.objects.filter(produit_commente=self)

        if notes.count() > 0:
            somme_notes = 0

            for note in notes:
                somme_notes += note.note
            note_recommandation = somme_notes / notes.count()
            import math

            return math.ceil(note_recommandation * 2) * 0.5
        else:
            return 0

    get_note_recommandation.short_description = 'Note'

    def increase_view_count(self):
        v = self.view_count
        v = v + 1
        self.view_count = v
        self.save()

    def image(self):
        from django.utils.html import format_html
        fichier_produit = FichierProduit.objects.filter(produit=self)

        if fichier_produit:
            return format_html(
                '<img style="object-fit: contain" width=50 height=50 src="http://localhost:8000'
                + fichier_produit[0].piece_jointe.url + '"/>')
        else:
            return format_html('<img src="" width=50 height=50 />')

    image.short_description = 'Image'
    image.allow_tags = True


class CrossSell(models.Model):
    produit = models.ForeignKey(Produit,
                                on_delete=models.CASCADE,
                                related_name="+")
    cross_sell = models.ForeignKey(Produit,
                                   on_delete=models.CASCADE,
                                   related_name="crosssell_set")


class FichierProduit(models.Model):
    class Meta:
        verbose_name = 'Fichier produit'
        verbose_name_plural = 'Fichiers produit'

    piece_jointe = models.FileField(upload_to='produits/pieces_jointes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.produit)


MODES_LIVRAISON_CHOICES = (
    ('LS', 'Livraison Standard'),
    ('EP', 'Envoie Postal Economique'),
)
MODES_PAIEMENT_CHOICES = (
    ('C', 'Par carte bancaire'),
    ('P', 'Paypal'),
    ('A', 'A la livraison'),
    ('V', 'Virement bancaire'),
)


class Commande(models.Model):
    class Meta:
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        default_permissions = ()

    date_commande = models.DateField("Date commande", auto_now_add=True)
    client = models.ForeignKey(Client,
                               verbose_name="Client",
                               on_delete=models.CASCADE)
    payee = models.BooleanField(default=False, verbose_name="Commande Payée")
    produits = models.ManyToManyField(Produit,
                                      verbose_name="Produits",
                                      through="ProduitCommande")
    mode_livraison = models.CharField("Mode de livraison",
                                      max_length=2,
                                      choices=MODES_LIVRAISON_CHOICES,
                                      default="LS")
    mode_paiement = models.CharField("Mode de paiement",
                                     max_length=1,
                                     choices=MODES_PAIEMENT_CHOICES,
                                     default="C")

    @property
    def total(self):
        t = 0

        for produit in self.produits.all():
            pc = ProduitCommande.objects.filter(produit=produit,
                                                commande=self)[0]
            t += produit.prix_produit * pc.qte

        if self.mode_livraison == "LS":
            prix_livraison = SiteSettings.getInstance().prix_livraison_standard
            t += prix_livraison

            return t
        else:
            return t

    def __str__(self):
        return str(self.date_commande)


class ProduitCommande(models.Model):
    class Meta:
        verbose_name = 'Produit de commande'
        verbose_name_plural = 'Produits de commande'
        unique_together = ("commande", "produit")

    commande = models.ForeignKey(to="Commande",
                                 verbose_name="Commande",
                                 on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit,
                                verbose_name="Produit",
                                on_delete=models.CASCADE)
    qte = models.PositiveIntegerField("Quantité", blank=True, default=1)

    def __str__(self):
        return f"Produit {self.produit}"

    def get_prix(self):
        return self.produit.prix_produit


class Panier(models.Model):
    class Meta:
        verbose_name = 'Panier'
        verbose_name_plural = 'Paniers'
        default_permissions = ()

    produits = models.ManyToManyField(Produit,
                                      verbose_name="Produits de panier",
                                      blank=True,
                                      through="ProduitPanier")
    client = models.OneToOneField(CustomUser,
                                  verbose_name="Client",
                                  on_delete=models.CASCADE)

    @property
    def total(self):
        t = 0

        for produit in self.produits.all():
            pp = ProduitPanier.objects.filter(produit=produit, panier=self)[0]
            t += produit.prix_produit * pp.qte

        return t

    def __str__(self):
        return f"Panier du client {self.client}"


class ProduitPanier(models.Model):
    class Meta:
        verbose_name = 'Produit de panier'
        verbose_name_plural = 'Produits de panier'
        unique_together = ("panier", "produit")

    panier = models.ForeignKey(Panier,
                               verbose_name="Panier",
                               on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit,
                                verbose_name="Produit",
                                on_delete=models.CASCADE)
    qte = models.PositiveIntegerField("Quantité", blank=True, default=1)

    def __str__(self):
        return f"Produit {self.produit}"


class NoteDeRecommandation(models.Model):
    class Meta:
        verbose_name = 'Note de recommandation'
        verbose_name_plural = 'Notes de recommandation'
        default_permissions = ()
        permissions = (("add_note_recommandation",
                        "Ajouter une note de recommandation"), )
        ordering = ['-id']

    note = models.PositiveSmallIntegerField(
        "Note", validators=[MinValueValidator(1),
                            MaxValueValidator(5)])
    commentaire = models.TextField("Commentaire", blank=True)
    date = models.DateTimeField("Date", auto_now=True)
    client = models.ForeignKey(Client,
                               verbose_name="Client",
                               on_delete=models.CASCADE)
    produit_commente = models.ForeignKey(Produit,
                                         verbose_name="Produit commenté",
                                         on_delete=models.CASCADE)

    def __str__(self):
        return f"Note: {self.note}, Produit: {self.produit_commente}"


class Contact(models.Model):
    fullname = models.CharField(verbose_name="FullName", max_length=40)
    email = models.EmailField(verbose_name="Email", max_length=40)
    subject = models.TextField(verbose_name="Subject", max_length=40)
    message = models.TextField(verbose_name='Message')

    def __str__(self):
        return f"{self.email} ,{self.subject}"

    def send_email(self):
        send_mail(
            '[E-commerce new Contact Mail]',
            'Bonjour,\n\nVous avez un nouveau contact.\nNom Complet : ' +
            self.fullname + '\nEmail : ' + self.email + '\nObjet : ' +
            self.subject + '\nMessage : ' + self.message,
            SiteSettings.getInstance().email_envoie_contact,
            [SiteSettings.getInstance().email_reception_contact],
            auth_user=SiteSettings.getInstance().email_envoie_contact,
            auth_password=SiteSettings.getInstance().password_envoie_contact,
            fail_silently=False,
        )


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)
        self.set_cache()

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def getInstance(cls):
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)

            if not created:
                obj.set_cache()

        return cache.get(cls.__name__)

    def set_cache(self):
        cache.set(self.__class__.__name__, self)


class SiteSettings(SingletonModel):
    class Meta:
        verbose_name = 'Paramètres du site'
        verbose_name_plural = 'Paramètres du site'

    nom_entreprise = models.CharField(max_length=50,
                                      verbose_name="Nom de l'entreprise")
    logo = models.ImageField(upload_to="images/logos",
                             verbose_name="Logo du header")
    favicon = models.ImageField(upload_to="images/logos")
    site_primary_color = ColorField(default="#3abbc2",
                                    verbose_name="Couleur primaire du site")
    modes_paiement = MultiSelectField(choices=MODES_PAIEMENT_CHOICES,
                                      max_choices=len(MODES_PAIEMENT_CHOICES),
                                      verbose_name="Modes de paiement")
    banque = models.CharField(
        blank=True,
        default="",
        max_length=50,
        help_text=
        "Le nom de la banque pour le mode de paiement du virement bancaire.")
    num_rib = models.CharField(
        blank=True,
        default="",
        max_length=100,
        verbose_name="Numéro RIB",
        help_text=
        "Le numéro RIB de du compte bancaire pour recevoir les virements bancaires."
    )
    paypal_client_id = models.CharField(
        blank=True,
        default="",
        max_length=120,
        verbose_name="Client ID du compte Paypal",
        help_text=
        "Saisir le client ID du compte Paypal à partir duquel vous souhaitez recevoir les paiements des clients."
    )
    prix_livraison_standard = models.DecimalField(max_digits=8,
                                                  decimal_places=2,
                                                  default=30)
    conditions_utilisation = models.FileField(
        upload_to="fichiers/conditions_utilisation",
        verbose_name="Conditions d'utilisation")
    about_us_text = RichTextField(verbose_name="Texte de la page About us")
    email_reception_contact = models.EmailField(
        verbose_name="Adresse mail de réception des messages de contact",
        default="exemple@gmail.com")
    email_envoie_contact = models.EmailField(
        verbose_name="Adresse mail d'envoie des message de contact",
        default="exemple@gmail.com")
    password_envoie_contact = models.CharField(
        max_length=20, verbose_name="Mot de passe de l'adresse mail d'envoie")
    tel_contact = models.CharField(max_length=20,
                                   verbose_name="Téléphone de contact",
                                   default="+212-xxxxxxxxx")
    adresse = models.CharField(max_length=50,
                               verbose_name="Adresse de l'entreprise")
    horaires_travail = models.CharField(max_length=45,
                                        verbose_name="Horaires de travail")
    lien_facebook = models.CharField(max_length=50,
                                     default="https://www.facebook.com/")
    lien_instagram = models.CharField(max_length=50,
                                      default="https://www.instagram.com/")
    lien_twitter = models.CharField(max_length=50,
                                    default="https://www.twitter.com/")

    def __str__(self):
        return "Paramètres du site"


class ImageSlider(models.Model):
    class Meta:
        verbose_name = 'Image du slider'
        verbose_name_plural = 'Images du slider'

    image = models.ImageField(upload_to="images/slider")
    site_settings = models.ForeignKey(SiteSettings, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.image)
