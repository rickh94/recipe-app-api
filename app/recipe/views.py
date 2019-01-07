from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Tag, Ingredient, Recipe
from recipe import serializers


class GenericRecipeViewset(viewsets.GenericViewSet):
    """Mixin for custom authentication options"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class BaseRecipeAttrViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, GenericRecipeViewset
):
    """Base ViewSet for user owned recipe attributes"""

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by("-name")

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage Ingredients in the database"""

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


def _params_to_ints(querystring):
    """Convert a list of string iD to a list of integers"""
    return [int(str_id) for str_id in querystring.split(",")]


def _filter_on_attr(queryset, attr_params, attr_name):
    if attr_params:
        # generate name of filter programatically
        filters = {f"{attr_name}__id__in": _params_to_ints(attr_params)}
        return queryset.filter(**filters)
    return queryset


class RecipeViewSet(viewsets.ModelViewSet, GenericRecipeViewset):
    """Manage recipes in the database"""

    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the recipes for the authenticated user"""
        queryset = self.queryset
        for attr_name in ["tags", "ingredients"]:
            attr_params = self.request.query_params.get(attr_name)
            queryset = _filter_on_attr(queryset, attr_params, attr_name)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return needed serializer class"""
        if self.action == "retrieve":
            return serializers.RecipeDetailSerializer
        elif self.action == "upload_image":
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
