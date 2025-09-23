from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include
from .views import (
                        UserCreateView,
                        UserRetrieveUpdateDestroyView,
                        UsertListView,
                        AdminViewSets,
                        UserVerifyView,
                        VerificationRequestViewSet
                    )
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.routers import DefaultRouter

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Add custom data
        data['user'] = {
            "id": self.user.id,
            "email": self.user.email,
            "role": self.user.role,
            "username": self.user.first_name,
        }
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

router = DefaultRouter()
router.register(r'admins', AdminViewSets, basename='admins')
router.register(r"verification-requests", VerificationRequestViewSet, basename="verification-requests")

urlpatterns = [
    path('users/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('users/register/', UserCreateView.as_view(), name='register'),
    path('users/<uuid:id>/retrieve/', UserRetrieveUpdateDestroyView.as_view(), name='retrieve_user'),
    path('users/list/', UsertListView.as_view(), name='list_users'),

    path('admin/user/<uuid:id>/verify/', UserVerifyView.as_view(), name='verify_user'),
    path('', include(router.urls)),
]
