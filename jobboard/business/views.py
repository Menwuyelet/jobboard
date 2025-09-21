from django.shortcuts import render
from .serializers import CategorySerializer, JobSerializer, ApplicationSerializer,JobApplicationStatusSerializer, NotificationSerializer
from rest_framework import generics, viewsets,  status, filters
from django_filters.rest_framework import DjangoFilterBackend
from accounts.permissions import IsAdmin, CanPost, IsOwnerOfApplication, IsJobOwner
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Categories, Jobs, Applications, Notifications
from rest_framework.response import Response

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for users to manage their own job postings.

    Permissions:
        - Create: Authenticated users with posting permissions.
        - Update/Delete: Only the job owner can modify their jobs.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    # permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    lookup_field = 'id'
    queryset = Categories.objects.all().prefetch_related('jobs')\
                                        .order_by('created_at')

class UserJobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for users to manage their own job postings.

    Permissions:
        - Create: Authenticated users with posting permissions.
        - Update/Delete: Only the job owner can modify their jobs.
    """
    serializer_class = JobSerializer
    lookup_field = "id"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['title', 'description']

    filterset_fields = ['category', 'is_active', 'working_area', 'longevity', 'type']

    def get_permissions(self):
        if self.action == "create":
            # return [AllowAny()]  
            return [IsAuthenticated(), CanPost()]
        return [IsAuthenticated(), IsJobOwner()]

    def get_queryset(self):
        user = self.request.user
        return Jobs.objects.filter(posted_by=user).select_related('category')\
                                                  .prefetch_related('applications')\
                                                  .order_by('-posted_at', '-is_active')

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(posted_by=user, is_active=True)

class JobDestroyView(generics.DestroyAPIView):
    """
    API to delete any job posting (admin only).
    """
    permission_classes = [IsAdmin]
    # permission_classes = [AllowAny]
    serializer_class = JobSerializer
    lookup_field = 'id'
    queryset = Jobs.objects.all()

class JobReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for all jobs available to the public.
    """
    permission_classes = [AllowAny]
    serializer_class = JobSerializer
    queryset = Jobs.objects.all().select_related('category', 'posted_by')\
                                    .prefetch_related('applications')\
                                    .order_by('-posted_at', '-is_active')
    lookup_field = "id"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['title', 'description']

    filterset_fields = ['category', 'is_active', 'working_area', 'longevity', 'type']


class UserApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for users to manage their own job applications.

    Permissions:
        - Create: Authenticated users.
        - Update/Delete: Only the applicant can modify their application.
    """
    serializer_class = ApplicationSerializer
    lookup_field = "id"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['job', 'status']

    filterset_fields = ['status',]

    def get_permissions(self):
        if self.action == "create":
            # return [AllowAny()]  
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOwnerOfApplication()]

    def get_queryset(self):
        user = self.request.user
        return Applications.objects.filter(user=user).prefetch_related('job')\
                                                     .order_by('-applied_at')

    def perform_create(self, serializer):
        user = self.request.user
        job = Jobs.objects.get(id=self.kwargs['id'])
        serializer.save(user=user, job=job)

class JobApplicationsListView(generics.ListAPIView):
    """
    List all applications for a specific job (job owner or admin only).
    """
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsJobOwner | IsAdmin]
    # permission_classes = [AllowAny]
    lookup_field = "job_id"

    def get_queryset(self):
        job_id = self.kwargs.get("job_id")
        job = Jobs.objects.get(id=job_id)

        # Check permission
        self.check_object_permissions(self.request, job)

        return Applications.objects.filter(job=job).prefetch_related('user')\
                                                   .order_by('-applied_at')

class JobApplicationStatusUpdateView(generics.UpdateAPIView):
    """
    Update the status of an application (job owner only).
    """
    serializer_class = JobApplicationStatusSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        # return Applications.objects.all()
        return Applications.objects.filter(job__posted_by=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        self.check_object_permissions(request, instance.job)

        status_value = request.data.get("status")
        if not status_value:
            return Response(
                {"detail": "Status field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        instance.status = status_value
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationListView(generics.ListAPIView):
    """
    List notifications for the authenticated user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['application', 'message']

    filterset_fields = ['is_read', 'application']
    def get_queryset(self):
        return Notifications.objects.filter(recipient=self.request.user).prefetch_related('application')\
                                                                        .order_by('is_read', '-created_at')


class NotificationDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single notification and mark it as read after wards.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Notifications.objects.filter(recipient=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Mark as read
        if not instance.is_read:
            instance.is_read = True
            instance.save(update_fields=['is_read'])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class NotificationDestroyView(generics.DestroyAPIView):
    """
    Delete a notification (recipient only).
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Notifications.objects.filter(recipient=self.request.user)
