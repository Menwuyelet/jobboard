# tests/test_jobs.py
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Jobs, Categories

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class JobAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # create users
        self.normal_user = User.objects.create_user(
            username="normaluser",
            email="user@example.com",
            password="Userpass@123",
            role="user"
        )
        self.owner_user = User.objects.create_user(
            username="owneruser",
            email="owner@example.com",
            password="Ownerpass@123",
            role="user",
            can_post_ajob=True
        )
        self.admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="Adminpass@123",
            role="admin",
            can_post_ajob=True
        )

        # generate tokens
        self.admin_tokens = get_tokens_for_user(self.admin_user)
        self.owner_tokens = get_tokens_for_user(self.owner_user)
        self.user_tokens = get_tokens_for_user(self.normal_user)

        # create categories
        self.category = Categories.objects.create(name="IT", description="IT Jobs")

        # create jobs
        self.job1 = Jobs.objects.create(title="Job1", description="Desc1", posted_by=self.owner_user)
        self.job2 = Jobs.objects.create(title="Job2", description="Desc2", posted_by=self.owner_user)

        # urls
        self.job_list_url = reverse("jobs-list")
        self.job_detail_url = reverse("jobs-detail", args=[self.job1.id])
        self.user_jobs_list_url = reverse("user-jobs-list")
        self.user_jobs_create_url = reverse("user-crate-jobs")
        self.user_jobs_update_url = reverse("user-jobs-update", args=[self.job1.id])
        self.user_jobs_delete_url = reverse("user-jobs-delete", args=[self.job1.id])
        self.job_destroy_url = reverse("job-destroy", args=[self.job1.id])

    def authenticate(self, tokens):
        """Helper to authenticate client with JWT access token"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

    # JobReadOnlyViewSet tests
    def test_public_can_list_jobs(self):
        response = self.client.get(self.job_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_public_can_retrieve_job(self):
        response = self.client.get(self.job_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.job1.title)

    # UserJobViewSet tests
    def test_user_can_list_their_jobs(self):
        self.authenticate(self.owner_tokens)
        response = self.client.get(self.user_jobs_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_user_can_create_job(self):
        self.authenticate(self.owner_tokens)
        payload = {
                    "title": "Backend Developer",
                    "description": "Responsible for building APIs and backend services.",
                    "location": "Addis Ababa, Ethiopia",
                    "working_area": "onsite",
                    "longevity": "contractual",
                    "type": "full-time",
        }
        response = self.client.post(self.user_jobs_create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Jobs.objects.filter(posted_by=self.owner_user).count(), 3)

    def test_user_can_update_their_job(self):
        self.authenticate(self.owner_tokens)
        payload = {"title": "Updated Job", "description": "Updated Desc"}
        response = self.client.patch(self.user_jobs_update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job1.refresh_from_db()
        self.assertEqual(self.job1.title, "Updated Job")

    def test_user_can_delete_their_job(self):
        self.authenticate(self.owner_tokens)
        response = self.client.delete(self.user_jobs_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Jobs.objects.filter(id=self.job1.id).exists())

    # JobDestroyView (admin-only) tests
    def test_admin_can_delete_any_job(self):
        self.authenticate(self.admin_tokens)
        response = self.client.delete(self.job_destroy_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_admin_cannot_delete_job(self):
        self.authenticate(self.user_tokens)
        response = self.client.delete(self.job_destroy_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # CategoryViewSet tests
    def test_admin_can_list_category(self):
        self.authenticate(self.admin_tokens)
        url = reverse("category-list")  # <-- use reverse instead of hardcoded URL
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_admin_cannot_list_category(self):
        self.authenticate(self.user_tokens)
        url = reverse("category-list")  # <-- use reverse
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_category(self):
        self.authenticate(self.admin_tokens)
        url = reverse("category-list")  # <-- use reverse
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_admin_cannot_list_category(self):
        self.authenticate(self.user_tokens)
        url = reverse("category-list")  # <-- use reverse
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_category_create_duplicate_name_fails(self):
        self.authenticate(self.admin_tokens)
        url = reverse("category-list")
        payload = {"name": "IT", "description": "Duplicate"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already exists", str(response.data))

    def test_category_can_be_created_by_admin(self):
        self.authenticate(self.admin_tokens)
        url = reverse("category-list")
        payload = {"name": "Finance", "description": "Finance Jobs"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Finance")