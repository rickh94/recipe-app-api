import os
from unittest import mock

from PIL import Image
import pytest

# from django.test import TestCase

from django.urls import reverse

from rest_framework import status

from core.models import Recipe
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

pytestmark = pytest.mark.django_db


# FIXTURES
@pytest.fixture
def recipes_url():
    """get recipes url"""
    return reverse("recipe:recipe-list")


@pytest.fixture
def detail_url():
    def _gen_detail_url(recipe_id):
        return reverse("recipe:recipe-detail", args=[recipe_id])

    return _gen_detail_url


@pytest.fixture
def image_upload_url():
    def _generate_image_upload_url(recipe_id):
        return reverse("recipe:recipe-upload-image", args=[recipe_id])

    return _generate_image_upload_url


# noinspection PyMethodMayBeStatic
class TestPublicRecipeAPI(object):
    def test_auth_required(self, public_client, recipes_url):
        """Test that authentication is required"""
        res = public_client.get(recipes_url)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class TestPrivateRecipeAPI(object):
    def test_retrieve_recipes(
        self,
        authenticated_client,
        recipes_url,
        recipe_with_tag_ingredient1,
        recipe_with_tag_ingredient2,
    ):

        res = authenticated_client.get(recipes_url)

        recipes = Recipe.objects.all().order_by("-id")

        serializer = RecipeSerializer(recipes, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_recipes_limited_to_user(
        self,
        authenticated_client,
        test_user,
        recipes_url,
        user2_recipe,
        recipe_with_tag_ingredient1,
    ):

        res = authenticated_client.get(recipes_url)

        recipes = Recipe.objects.filter(user=test_user)
        serializer = RecipeSerializer(recipes, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 1
        assert res.data == serializer.data

    def test_view_recipe_detail(
        self, detail_url, authenticated_client, recipe_with_tag_ingredient1
    ):
        """Test viewing a recipe detail"""
        recipe = recipe_with_tag_ingredient1
        url = detail_url(recipe.id)
        res = authenticated_client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        assert res.data == serializer.data

    def test_create_basic_recipe(self, authenticated_client, recipes_url):
        """Test creating recipe"""
        payload = {"title": "Chocolate cheesecake", "time_minutes": 30, "price": 5.00}

        res = authenticated_client.post(recipes_url, payload)
        assert res.status_code == status.HTTP_201_CREATED

        recipe = Recipe.objects.get(id=res.data["id"])

        for key, value in payload.items():
            assert value == getattr(recipe, key)

    def test_create_recipe_with_tags(
        self, authenticated_client, recipes_url, test_user, sample_tag1, sample_tag2
    ):
        """Test creating a recipe with tags"""
        payload = {
            "title": "Avocado Lime Cheesecake",
            "tags": [sample_tag1.id, sample_tag2.id],
            "time_minutes": 60,
            "price": 20.00,
        }

        res = authenticated_client.post(recipes_url, payload)
        assert res.status_code == status.HTTP_201_CREATED

        recipe = Recipe.objects.get(id=res.data["id"])
        tags = recipe.tags.all()
        assert tags.count() == 2
        assert sample_tag1 in tags
        assert sample_tag2 in tags

    def test_create_recipe_with_ingredients(
        self,
        authenticated_client,
        recipes_url,
        test_user,
        sample_ingredient1,
        sample_ingredient2,
    ):
        """Test creating a recipe with ingredients"""
        payload = {
            "title": "Thai Prawn Red Curry",
            "ingredients": [sample_ingredient1.id, sample_ingredient2.id],
            "time_minutes": 20,
            "price": 7.00,
        }
        res = authenticated_client.post(recipes_url, payload)
        assert res.status_code == status.HTTP_201_CREATED

        recipe = Recipe.objects.get(id=res.data["id"])
        ingredients = recipe.ingredients.all()

        assert ingredients.count() == 2
        assert sample_ingredient2 in ingredients
        assert sample_ingredient1 in ingredients

    def test_partial_update_recipe(
        self, authenticated_client, detail_url, recipe_with_tag_ingredient1, sample_tag2
    ):
        """Test updating a recipe with patch"""
        payload = {"title": "Chicken Tikka", "tags": [sample_tag2.id]}
        url = detail_url(recipe_with_tag_ingredient1.id)
        authenticated_client.patch(url, payload)

        recipe_with_tag_ingredient1.refresh_from_db()

        assert recipe_with_tag_ingredient1.title == payload["title"]
        tags = recipe_with_tag_ingredient1.tags.all()
        assert len(tags) == 1
        assert sample_tag2 in tags

    def test_full_update_recipe(
        self, authenticated_client, detail_url, test_user, recipe_with_tag_ingredient1
    ):
        """Test updating a recipe with put"""
        payload = {"title": "Spaghetti Carbonara", "time_minutes": 25, "price": 5.00}

        authenticated_client.put(detail_url(recipe_with_tag_ingredient1.id), payload)
        recipe_with_tag_ingredient1.refresh_from_db()

        for key, value in payload.items():
            assert value == getattr(recipe_with_tag_ingredient1, key)

        assert recipe_with_tag_ingredient1.tags.all().count() == 0


class TestRecipeImageUpload(object):
    def test_upload_image_to_recipe(
        self, sample_recipe1, authenticated_client, image_upload_url, tmp_path
    ):
        """Test uploading image to recipe"""
        url = image_upload_url(sample_recipe1.id)
        ntf = tmp_path / "test.jpg"
        img = Image.new("RGB", (10, 10))
        with ntf.open("wb") as the_image:
            img.save(the_image, format="JPEG")

        with ntf.open("rb") as the_image:
            res = authenticated_client.post(
                url, {"image": the_image}, format="multipart"
            )

        sample_recipe1.refresh_from_db()

        assert res.status_code == status.HTTP_200_OK
        assert "image" in res.data
        assert os.path.exists(sample_recipe1.image.path)

    def test_upload_image_bad_request(
        self, authenticated_client, sample_recipe1, image_upload_url
    ):
        """Test uploading an invalid image"""
        url = image_upload_url(sample_recipe1.id)
        res = authenticated_client.post(url, {"image": "notimage"}, format="multipart")

        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_filter_recipes_by_tags(
        self,
        sample_recipe1_serializer,
        recipe_with_tag_ingredient1_serializer,
        recipe_with_tag_ingredient2_serializer,
        sample_tag1,
        sample_tag2,
        authenticated_client,
        recipes_url,
    ):
        """Test returning recipes with specific tags"""
        res = authenticated_client.get(
            recipes_url, {"tags": f"{sample_tag1.id},{sample_tag2.id}"}
        )

        assert recipe_with_tag_ingredient1_serializer.data in res.data
        assert recipe_with_tag_ingredient2_serializer.data in res.data
        assert sample_recipe1_serializer.data not in res.data

    def test_filter_recipes_by_ingredients(
        self,
        sample_recipe1_serializer,
        recipe_with_tag_ingredient1_serializer,
        recipe_with_tag_ingredient2_serializer,
        sample_ingredient1,
        sample_ingredient2,
        authenticated_client,
        recipes_url,
    ):
        """Test returning recipes with specific ingredients"""
        res = authenticated_client.get(
            recipes_url,
            {"ingredients": f"{sample_ingredient1.id},{sample_ingredient2.id}"},
        )

        assert recipe_with_tag_ingredient1_serializer.data in res.data
        assert recipe_with_tag_ingredient2_serializer.data in res.data
        assert sample_recipe1_serializer.data not in res.data
