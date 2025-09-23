from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import VerificationRequest

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

    def test_user_can_create_verification_request(self):
        self.authenticate(self.owner_tokens)
        url = reverse("verification-requests-list")
        payload = {"reason": "I want to verify my account"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(VerificationRequest.objects.count(), 1)
        vr = VerificationRequest.objects.first()
        self.assertEqual(vr.user, self.owner_user)
        self.assertEqual(vr.status, "pending")

    def test_user_cannot_create_multiple_pending_requests(self):
        self.authenticate(self.user_tokens)
        url = reverse("verification-requests-list")
        self.client.post(url, {"reason": "first request"}, format="json")
        response = self.client.post(url, {"reason": "second request"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("pending", response.data["detail"].lower())

    def test_admin_can_list_all_requests(self):
        # create request as normal user
        VerificationRequest.objects.create(user=self.normal_user, reason="verify me")
        self.authenticate(self.admin_tokens)
        url = reverse("verification-requests-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_user_can_only_see_their_own_requests(self):
        VerificationRequest.objects.create(user=self.normal_user, reason="user req")
        VerificationRequest.objects.create(user=self.owner_user, reason="owner req")

        self.authenticate(self.user_tokens)
        url = reverse("verification-requests-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # should only return requests belonging to normal_user
        for req in response.data['results']:
            self.assertEqual(req["user"], self.normal_user.id)

    def test_admin_can_approve_request(self):
        req = VerificationRequest.objects.create(user=self.normal_user, reason="please verify")
        self.authenticate(self.admin_tokens)
        url = reverse("verification-requests-detail", args=[req.id])
        response = self.client.patch(url, {"status": "approved"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        req.refresh_from_db()
        self.assertEqual(req.status, "approved")

    def test_non_admin_cannot_update_request_status(self):
        req = VerificationRequest.objects.create(user=self.owner_user, reason="need verify")
        self.authenticate(self.owner_tokens)
        url = reverse("verification-requests-detail", args=[req.id])
        response = self.client.patch(url, {"status": "approved"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        req.refresh_from_db()
        self.assertEqual(req.status, "pending")

    def test_invalid_status_rejected(self):
        req = VerificationRequest.objects.create(user=self.owner_user, reason="invalid test")
        self.authenticate(self.admin_tokens)
        url = reverse("verification-requests-detail", args=[req.id])
        response = self.client.patch(url, {"status": "wrongstatus"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        req.refresh_from_db()
        self.assertEqual(req.status, "pending")