from django.shortcuts import render
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework import mixins
from recepies.models import Tag, Recipe, Ingredient, Favorite, Shoplist
from users.models import User, Follow
from .serializers import TagSerializer, RecipeCreateSerializer, RecipeShowSerializer, FollowSerializer, IngredientShowSerializer, FollowShowSerializer, RecipeFollowShowSerializer
from .pagination import CustomPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from .permissions import IsAuthorOrReadOnlyPermission, IsAdminOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from utils.functions import count_ingredients
from django.template.loader import render_to_string
# from weasyprint import HTML
from .filters import RecipeFilter, IngredientFilter

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

@api_view(['GET',])
@permission_classes([permissions.IsAuthenticated])
def download_pdf(request):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    lines = [
        "Line 1",
        "Line 2"
    ]

    for line in lines:
        textob.textLine(line)
    
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='recipes.pdf')

def some_view(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="hello.pdf")

class TagViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeShowSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = IngredientShowSerializer
    pagination_class = None
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (IsAdminOrReadOnly,)

class FollowViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet    
    ):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, **kwargs)

@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def follow(request, pk):
    user = get_object_or_404(User, username=request.user.username)
    following = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        if user.id == following.id:
            return Response('Нельзя подписаться на самого себя', status=status.HTTP_400_BAD_REQUEST)
        elif Follow.objects.filter(user=user, following=following).exists():
            return Response('Вы уже подписаны на этого пользователя', status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.create(user=user, following=following)
        to_serializer = User.objects.get(username=following)
        serializer = FollowShowSerializer(to_serializer, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        try:
            subscription = Follow.objects.get(user=user, following=following)
        except ObjectDoesNotExist:
            return Response('Вы не подписаны на этого пользователя', status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return HttpResponse ('Вы отписались от пользователя', status=status.HTTP_204_NO_CONTENT)

class FollowListViewsSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = FollowShowSerializer
    queryset = User.objects.all()
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)

@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def fav_recipe(request, id):
    user = get_object_or_404(User, username=request.user.username)
    recipe = get_object_or_404(Recipe, pk=id)

    if request.method == 'POST':
        Favorite.objects.create(user=user, recipe=recipe)
        serializer = RecipeFollowShowSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        fav = Favorite.objects.filter(user=user, recipe=recipe)
        fav.delete()
        return HttpResponse (status=status.HTTP_204_NO_CONTENT)

@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def add_delete_shopcart(request, id):
    user = get_object_or_404(User, username=request.user.username)
    recipe = get_object_or_404(Recipe, pk=id)

    if request.method == 'POST':
        Shoplist.objects.create(user=user, item=recipe)
        serializer = RecipeFollowShowSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        fav = Shoplist.objects.get(user=user, item=recipe)
        fav.delete()
        return HttpResponse (status=status.HTTP_204_NO_CONTENT)

# def download_shopping_cart(request, id):
#     ingredients = count_ingredients(request.user)
#     html_template = render_to_string('recipes/pdf_template.html',
#                                         {'ingredients': ingredients})
#     html = HTML(string=html_template)
#     result = html.write_pdf()
#     response = HttpResponse(result, content_type='application/pdf;')
#     response['Content-Disposition'] = 'inline; filename=shopping_list.pdf'
#     response['Content-Transfer-Encoding'] = 'binary'
#     return response
