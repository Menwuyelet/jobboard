from rest_framework import generics, viewsets, response, status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsAdmin, IsSelf
from .serializers import UserSerializer, VerificationRequestSerializer
from .models import User, VerificationRequest
from django_filters.rest_framework import DjangoFilterBackend


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

class VerificationRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user verification requests.

    Permissions:
        - Authenticated users can:
            - Create their own verification requests (only if they don’t already have a pending one).
            - View their own requests.
        - Admin users can:
            - View all verification requests.
            - Approve or deny requests.

    Actions:
        - get_queryset:
            - Admins: See all requests (ordered by creation date).
            - Users: See only their own requests (ordered by creation date).

        - create:
            - Ensures a user cannot submit more than one pending request at a time.
            - Creates a new verification request for the current user.

        - update:
            - Restricted to admins only.
            - Allows admins to change the status of a request to "approved" or "denied".
            - Invalid status values return a 400 response.
    """
    serializer_class = VerificationRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['status']
    def get_queryset(self):
        if self.request.user.role=='admin':
            return VerificationRequest.objects.all().order_by('created_at')

        return VerificationRequest.objects.filter(user=self.request.user).order_by('created_at')

    def create(self, request, *args, **kwargs):
        if VerificationRequest.objects.filter(user=request.user, status="pending").exists():
            return response.Response({"detail": "You already have a pending request."}, status=status.HTTP_400_BAD_REQUEST)

        data = {"user": request.user, "reason": request.data.get("reason", "")}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return response.Response({"detail": "Verification request submitted."}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.role=='admin':
            return response.Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        status_choice = request.data.get("status")
        if status_choice not in ["approved", "denied"]:
            return response.Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        instance.status = status_choice
        instance.save()

        return response.Response({"detail": f"Request {status_choice}."})
