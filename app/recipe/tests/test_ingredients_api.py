import pytest
from django.urls import reverse

from rest_framework import status

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

pytestmark = pytest.mark.django_db


@pytest.fixture
def ingredients_url():
    return reverse("recipe:ingredient-list")


class TestPublicIngredientsAPI(object):
    """Test the publicly available ingredients api"""

    def test_login_required(self, public_client, ingredients_url):
        """Test that login is required to access the endpoint"""
        res = public_client.get(ingredients_url)
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


# noinspection PyUnusedLocal
class TestPrivateIngredientsAPI(object):
    """Test the private ingredients API"""

    def test_retrieve_ingredient_list(
        self,
        authenticated_client,
        sample_ingredient1,
        sample_ingredient2,
        ingredients_url,
    ):
        """Test retrieving a list of ingredients"""
        res = authenticated_client.get(ingredients_url)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_ingredients_limited_to_user(
        self,
        sample_ingredient1,
        user2_ingredient,
        authenticated_client,
        ingredients_url,
    ):
        """Test that only ingredients for the authenticated user are returned"""
        res = authenticated_client.get(ingredients_url)

        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 1
        assert res.data[0]["name"] == sample_ingredient1.name

    def test_create_ingredient_successful(
        self, authenticated_client, ingredients_url, test_user
    ):
        """Test create a new ingredient"""
        payload = {"name": "Cabbage"}
        authenticated_client.post(ingredients_url, payload)

        assert Ingredient.objects.filter(user=test_user, name=payload["name"]).exists()

    def test_create_ingredient_invalid(self, authenticated_client, ingredients_url):
        """Test creating invalid ingredient fails"""
        payload = {"name": ""}
        res = authenticated_client.post(ingredients_url, payload)

        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_ingredients_assigned_to_recipes(
        self,
        sample_ingredient1,
        recipe_with_tag_ingredient1,
        unassigned_ingredient,
        authenticated_client,
        ingredients_url,
    ):
        """Test filtering ingredients by those assigned to recipes"""
        res = authenticated_client.get(ingredients_url, {"assigned_only": 1})

        assigned_serializer = IngredientSerializer(sample_ingredient1)
        unassigned_serializer = IngredientSerializer(unassigned_ingredient)

        assert assigned_serializer.data in res.data, "Should return assigned ingredient"
        assert (
            unassigned_serializer.data not in res.data
        ), "Should not return unassigned ingredient"
