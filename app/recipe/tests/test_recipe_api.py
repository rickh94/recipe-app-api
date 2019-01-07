import pytest
from django.contrib.auth import get_user_model

from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe

from recipe.serializers import RecipeSerializer


@pytest.fixture
def recipes_url():
    """get recipes url"""
    return reverse("recipe:recipe-list")


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {"title": "Sample Recipe", "time_minutes": 10, "price": 5.00}
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


@pytest.fixture
def public_client():
    return APIClient()


@pytest.fixture
def test_user():
    return get_user_model().objects.create_user(
        "barack@whitehouse.gov", "The 44th President"
    )


@pytest.fixture
def test_user2():
    return get_user_model().objects.create_user(
        "michelle@whitehouse.gov", "The 44th First Lady"
    )


@pytest.fixture
def authenticated_client(test_user):
    client = APIClient()
    client.force_authenticate(test_user)
    return client


# noinspection PyMethodMayBeStatic
class PublicRecipeAPITests(object):
    def test_auth_required(self, public_client, recipes_url):
        """Test that authentication is required"""
        res = public_client.get(recipes_url)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED


# noinspection PyMethodMayBeStatic
class PrivateRecipeAPITests(object):
    def test_retrieve_recipes(self, authenticated_client, test_user, recipes_url):
        sample_recipe(user=test_user)
        sample_recipe(user=test_user)

        res = authenticated_client.get(recipes_url)

        recipes = Recipe.objects.all().order_by("-id")

        serializer = RecipeSerializer(recipes, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_recipes_limited_to_user(
        self, authenticated_client, test_user, recipes_url, test_user2
    ):
        sample_recipe(user=test_user2)
        sample_recipe(user=test_user)

        res = authenticated_client.get(recipes_url)

        recipes = Recipe.objects.filter(user=test_user)
        serializer = RecipeSerializer(recipes, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 1
        assert res.data == serializer.data
