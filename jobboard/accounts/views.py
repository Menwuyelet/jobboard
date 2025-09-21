from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsAdmin, IsSelf
from .serializers import UserSerializer
from .models import User


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a single regular user.

    Permissions:
        - User can access their own data (IsSelf)
        - Admins can access any user data (IsAdmin)
    """
    serializer_class = UserSerializer
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated, IsSelf | IsAdmin]
    lookup_field = 'id'

    def get_queryset(self):
        """Return queryset of regular users only."""
        return User.objects.filter(role='user')

    def perform_update(self, serializer):
        """Save updates to the user instance."""
        serializer.save()

    def perform_destroy(self, instance):
        """Delete the user instance."""
        instance.delete()

class UserCreateView(generics.CreateAPIView):
    """
    API view to create a new regular user.

    Permissions:
        - Open to any user (AllowAny)
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        """Assign 'user' role when creating a new user."""
        serializer.save(role='user')

class UsertListView(generics.ListAPIView):
    """
    API view to list all regular users.

    Permissions:
        - Only admins can access this endpoint.
    """
    serializer_class = UserSerializer
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.filter(role='user').order_by('first_name')

class UserVerifyView(generics.UpdateAPIView):
    """
    API view to toggle a user's permission to post a job.

    Permissions:
        - Only admins can access this endpoint.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'

    def get_queryset(self):
        return User.objects.filter(role='user')
    
    def perform_update(self, serializer):
        user = serializer.instance 
        if not user.can_post_ajob:
            serializer.save(can_post_ajob=True)
        else:
            serializer.save(can_post_ajob=False)

class AdminViewSets(viewsets.ModelViewSet):
    """
    API viewset for managing admin users.

    Permissions:
        - Only admins can access this endpoint.
    """
    permission_classes = [IsAdmin]
    # permission_classes = [AllowAny]
    serializer_class = UserSerializer
    lookup_field = 'id'
    queryset = User.objects.filter(role='admin').order_by('first_name')

    def perform_create(self, serializer):
        role = "admin"
        serializer.save(role=role, can_post_ajob=True)
    
    def perform_destroy(self, instance):
        instance.delete()
