from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, filters, pagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.db.models import Q

from .models import *
from .serializers import *


class ProduitPagination(pagination.PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 9


#  from rest_framework import permissions

# class IsCurrentUser(permissions.BasePermission):
#     message = 'Adding customers not allowed.'

#     def has_object_permission(self, request, view, obj):
#         return obj.user == request.user


# APIs Clients
class ClientCreateList(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ClientDetailUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class CustomUserList(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class CustomUserDetail(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


# APIs Produits
class ProduitsList(generics.ListAPIView):
    def get_queryset(self):
        queryset = Produit.objects.all()
        nouveau = self.request.query_params.get('nouveau')

        if nouveau is not None:
            queryset = queryset.filter(nouveau=nouveau)

        return queryset

    serializer_class = ProduitSerializer
    pagination_class = ProduitPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'nom_produit', 'description_produit', 'categorie__libelle'
    ]
    ordering_fields = ['prix_produit', 'view_count', 'date_ajout']


class ProduitDetail(generics.RetrieveAPIView):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

    def get(self, request, *args, **kwargs):
        p = Produit.objects.get(id=self.kwargs["pk"])
        p.increase_view_count()
        c = p.categorie
        c.increase_view_count()

        return Response(self.get_serializer(p).data)


class ProduitAjouter(generics.CreateAPIView):
    queryset = Produit.objects.all()
    serializer_class = AjouterProduitSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class FichiersProduitList(generics.ListAPIView):
    queryset = FichierProduit.objects.all()
    serializer_class = FichierProduitSerializer


class FichierProduitDetail(generics.RetrieveAPIView):
    queryset = FichierProduit.objects.all()
    serializer_class = FichierProduitSerializer

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class FichierProduitAjouter(generics.CreateAPIView):
    queryset = Produit.objects.all()
    serializer_class = FichierProduitSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# APIs Categorie
class CategoriesList(generics.ListAPIView):
    queryset = Categorie.objects.filter(level=0)
    serializer_class = CategorieSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['view_count']

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CategorieDetail(generics.RetrieveAPIView):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer2

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CategorieDetail2(generics.RetrieveAPIView):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# API Produits par Categorie
class ProduitsCategorie(generics.ListAPIView):
    def get_queryset(self):
        id = self.kwargs["pk"]
        categorie = Categorie.objects.get(id=id)
        categorie.get_family_tree(categorie)
        categories = categorie.child_categories

        return Produit.objects.filter(categorie__in=categories)

    serializer_class = ProduitSerializer
    pagination_class = ProduitPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['nom_produit', 'description_produit']

    def get(self, request, *args, **kwargs):
        c = Categorie.objects.get(id=self.kwargs["pk"])
        c.increase_view_count()

        return super().get(request, *args, **kwargs)


# APIs Paniers
class AjouterAuPanier(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProduitPanierSerializer2

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class SupprimerDuPanier(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProduitPanierSerializer2
    queryset = ProduitPanier.objects.all()

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class NewPanier(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PanierSerializer3
    queryset = Panier.objects.all()

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("client")
        user = generics.get_object_or_404(CustomUser, id=user_id)
        Client.objects.create(customuser_ptr=user,
                              first_name=user.first_name,
                              last_name=user.last_name,
                              email=user.email,
                              username=user.username,
                              password=user.password)

        return super().create(request, *args, **kwargs)


class PanierDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PanierSerializer2
    queryset = Panier.objects.all()

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PorduitPanierDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProduitPanierSerializer2
    queryset = ProduitPanier.objects.all()

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PorduitPanierModifier(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProduitPanierSerializer2
    queryset = ProduitPanier.objects.all()

    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)


# APIs Commandes
class NewCommade(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer2


class AjouterProduitCommande(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ProduitCommande.objects.all()
    serializer_class = ProduitCommmandeSerializer2


class CommandesClient(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommandeSerializer

    def get_queryset(self):
        queryset = Commande.objects.filter(client=self.kwargs["pk"])

        return queryset


# APIs Notes de recommandation
class AjouterNote(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = NoteDeRecommandation.objects.all()
    serializer_class = NoteSerializer2

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class NotesList(generics.ListAPIView):
    queryset = NoteDeRecommandation.objects.all()
    serializer_class = NoteSerializer

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# API Notes d'un produit
class NotesProduit(generics.ListAPIView):
    def get_queryset(self):
        queryset = NoteDeRecommandation.objects.filter(
            produit_commente=self.kwargs["pk"])

        return queryset

    serializer_class = NoteSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date']

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# APIs Contact Us
class ContactUs(generics.CreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# Site settings
class ImageSliderListe(generics.ListCreateAPIView):
    queryset = ImageSlider.objects.all()
    serializer_class = ImageSliderSerializer


class SiteSettingsDetail(APIView):
    def get(self, request):
        return Response(
            SiteSettingsSerializer(SiteSettings.getInstance()).data)

# ******* Set By yattara ********
#  Add search fonctionnality
@api_view(['POST'])
def search(request):
    query = request.data.get('query', '')

    if query:
        produits = Produit.objects.filter(
            Q(nom_produit__icontains=query)
            | Q(description_produit__icontains=query))
        serializer = ProduitSerializer(produits, many=True)

        return Response(serializer.data)
    else:
        return Response({'produits': []})

class CreateClientView(generics.CreateAPIView):

    model = Client
    permission_classes = [
        AllowAny # Or anon users can't register
    ]
    serializer_class = ClientSerializer
