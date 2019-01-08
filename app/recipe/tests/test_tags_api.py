import pytest
from django.urls import reverse
from recipe.serializers import TagSerializer
from rest_framework import status

from core.models import Tag

pytestmark = pytest.mark.django_db


@pytest.fixture
def tags_url():
    return reverse("recipe:tag-list")


class TestPublicTagsAPI(object):
    """Test the publicly available tags API"""

    def test_login_required(self, public_client, tags_url):
        """Test that login is required for retrieving tags"""
        res = public_client.get(tags_url)
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


# noinspection PyUnusedLocal
class TestPrivateTagsAPI(object):
    """Test the authorized tags api"""

    def test_retrieve_tags(
        self, sample_tag1, sample_tag2, tags_url, authenticated_client
    ):
        """Test retrieving tags"""

        res = authenticated_client.get(tags_url)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_tags_limited_to_user(
        self, test_user2, authenticated_client, sample_tag1, user2_tag, tags_url
    ):
        """Test that tags returned are for the authenticated user"""

        res = authenticated_client.get(tags_url)

        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 1
        assert res.data[0]["name"] == sample_tag1.name
        assert user2_tag not in res.data

    def test_create_tag_successful(self, authenticated_client, test_user, tags_url):
        """Test creating a new tag"""
        payload = {"name": "Test tag"}
        authenticated_client.post(tags_url, payload)

        assert Tag.objects.filter(user=test_user, name=payload["name"]).exists()

    def test_create_tag_invalid(self, authenticated_client, tags_url):
        """Test creating a new tag with invalid payload"""
        payload = {"name": ""}
        res = authenticated_client.post(tags_url, payload)

        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_tags_assigned_to_recipes(
        self,
        sample_tag1,
        unassigned_tag,
        recipe_with_tag_ingredient1,
        authenticated_client,
        tags_url,
    ):
        """Test filtering tags by those assigned to recipes"""
        res = authenticated_client.get(tags_url, {"assigned_only": 1})

        assigned_serializer = TagSerializer(sample_tag1)
        unassigned_serializer = TagSerializer(unassigned_tag)

        assert assigned_serializer.data in res.data, "Should return assigned ingredient"
        assert (
            unassigned_serializer.data not in res.data
        ), "Should not return unassigned ingredient"
