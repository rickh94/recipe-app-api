import pytest
from core.models import Ingredient, Recipe, Tag
from django.contrib.auth import get_user_model
from recipe.serializers import RecipeSerializer
from rest_framework.test import APIClient


# ----------------------- USERS ----------------------------
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


# --------------------- CLIENTS -----------------------------
@pytest.fixture
def public_client():
    return APIClient()


@pytest.fixture
def authenticated_client(test_user):
    client = APIClient()
    client.force_authenticate(test_user)
    return client


# --------------------- INGREDIENTS -----------------------
@pytest.fixture
def sample_ingredient1(test_user):
    return _sample_ingredient(user=test_user, name="Curry Powder")


@pytest.fixture
def sample_ingredient2(test_user):
    return _sample_ingredient(user=test_user, name="Eggplant")


@pytest.fixture
def user2_ingredient(test_user2):
    return _sample_ingredient(user=test_user2, name="Pineapple")


@pytest.fixture
def unassigned_ingredient(test_user):
    return _sample_ingredient(user=test_user, name="Apples")


# ------------------------ TAGS ------------------------
@pytest.fixture
def sample_tag1(test_user):
    return _sample_tag(user=test_user, name="Vegan")


@pytest.fixture
def unassigned_tag(test_user):
    return _sample_tag(user=test_user, name="Unassigned")


@pytest.fixture
def sample_tag2(test_user):
    return _sample_tag(user=test_user, name="Vegetarian")


@pytest.fixture
def user2_tag(test_user2):
    return _sample_tag(user=test_user2)


# ------------------ RECIPES --------------------------------
@pytest.fixture
def user2_recipe(test_user2):
    return _sample_recipe(user=test_user2)


@pytest.fixture
def sample_recipe1(test_user):
    recipe = _sample_recipe(user=test_user)
    yield recipe
    recipe.image.delete()


@pytest.fixture
def recipe_with_tag_ingredient2(test_user, sample_tag2, sample_ingredient2):
    recipe = _sample_recipe(user=test_user, title="Aubergine with tahini")
    recipe.tags.add(sample_tag2)
    recipe.ingredients.add(sample_ingredient2)
    return recipe


@pytest.fixture
def recipe_with_tag_ingredient1(test_user, sample_tag1, sample_ingredient1):
    recipe = _sample_recipe(user=test_user, title="Thai vegetable curry")
    recipe.tags.add(sample_tag1)
    recipe.ingredients.add(sample_ingredient1)
    return recipe


# ----------------- SERIALIZERS ------------------------------
@pytest.fixture
def sample_recipe1_serializer(sample_recipe1):
    return RecipeSerializer(sample_recipe1)


@pytest.fixture
def recipe_with_tag_ingredient1_serializer(recipe_with_tag_ingredient1):
    return RecipeSerializer(recipe_with_tag_ingredient1)


@pytest.fixture
def recipe_with_tag_ingredient2_serializer(recipe_with_tag_ingredient2):
    return RecipeSerializer(recipe_with_tag_ingredient2)


# ----------- HELPER FUNCTIONS ----------------
def _sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {"title": "Sample Recipe", "time_minutes": 10, "price": 5.00}
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


def _sample_tag(user, name="Main course"):
    return Tag.objects.create(user=user, name=name)


def _sample_ingredient(user, name="Cinnamon"):
    return Ingredient.objects.create(user=user, name=name)
