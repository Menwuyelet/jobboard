from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresponseh": str(refresh),
        "access": str(refresh.access_token),
    }

class UserAPITests(TestCase):
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

    def authenticate(self, tokens):
        """Helper to authenticate client with JWT access token"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

    def test_register_user_success(self):
        url = reverse("register")
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "Newpass@123",
            "first_name": "New",
            "last_name": "User",
            "gender": "male",
            "nationality": "Ethiopian",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "newuser")

    def test_get_user_detail(self):
        self.authenticate(self.user_tokens)
        url = reverse("retrieve_user", args=[self.normal_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.normal_user.email)

    def test_update_user_profile(self):
        self.authenticate(self.user_tokens)
        url = reverse("retrieve_user", args=[self.normal_user.id])
        payload = {"first_name": "Updated"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.first_name, "Updated")

    def test_delete_user(self):
        self.authenticate(self.user_tokens)
        url = reverse("retrieve_user", args=[self.normal_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.normal_user.id).exists())

    def test_admin_can_list_users(self):
        self.authenticate(self.admin_tokens)
        url = reverse("list_users")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_non_admin_cannot_list_users(self):
        self.authenticate(self.user_tokens)
        url = reverse("list_users")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_toggle_can_post_job(self):
        self.authenticate(self.admin_tokens)
        url = reverse("verify_user", args=[self.normal_user.id])
        response = self.client.patch(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_user.refresh_from_db()
        self.assertTrue(self.normal_user.can_post_ajob)

    # --- Admin CRUD via AdminViewSets ---
    def test_admin_create_admin_user(self):
        self.authenticate(self.admin_tokens)
        url = reverse("admins-list")
        payload = {
            "username": "secondadmin",
            "email": "secondadmin@example.com",
            "password": "Admin@1234",
            "first_name": "Second",
            "last_name": "Admin",
            "gender": "male"
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_user = User.objects.get(username="secondadmin")
        self.assertEqual(created_user.role, "admin")
        self.assertTrue(created_user.can_post_ajob)

    def test_admin_update_admin_user(self):
        self.authenticate(self.admin_tokens)
        url = reverse("admins-detail", args=[self.admin_user.id])
        payload = {"first_name": "UpdatedAdmin"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.first_name, "UpdatedAdmin")

    def test_admin_delete_admin_user(self):
        self.authenticate(self.admin_tokens)
        url = reverse("admins-detail", args=[self.admin_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.admin_user.id).exists())