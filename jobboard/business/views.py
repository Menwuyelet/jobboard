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
        permission_classes = [IsAuthenticated, IsAdmin]
        # permission_classes = [AllowAny]
        serializer_class = CategorySerializer
        lookup_field = 'id'
        queryset = Categories.objects.all().order_by('created_at')

class UserJobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    lookup_field = "id"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['title', 'description']

    filterset_fields = ['category', 'is_active']

    def get_permissions(self):
        if self.action == "create":
            # return [AllowAny()]  
            return [IsAuthenticated(), CanPost()]
        return [IsAuthenticated(), IsJobOwner()]

    def get_queryset(self):
        user = self.request.user
        return Jobs.objects.filter(posted_by=user).order_by('-posted_at', '-is_active')

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(posted_by=user, is_active=True)

class JobDestroyView(generics.DestroyAPIView):
        permission_classes = [IsAdmin]
        # permission_classes = [AllowAny]
        serializer_class = JobSerializer
        lookup_field = 'id'
        queryset = Jobs.objects.all()

class JobReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
        permission_classes = [AllowAny]
        serializer_class = JobSerializer
        queryset = Jobs.objects.all().order_by('-posted_at', '-is_active')
        lookup_field = "id"
        filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

        search_fields = ['title', 'description']

        filterset_fields = ['category', 'is_active', 'posted_by']


class UserApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    lookup_field = "id"

    def get_permissions(self):
        if self.action == "create":
            # return [AllowAny()]  
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOwnerOfApplication()]

    def get_queryset(self):
        user = self.request.user
        return Applications.objects.filter(user=user).order_by('-applied_at')

    def perform_create(self, serializer):
        user = self.request.user
        job = Jobs.objects.get(id=self.kwargs['id'])
        serializer.save(user=user, job=job)

class JobApplicationsListView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsJobOwner | IsAdmin]
    # permission_classes = [AllowAny]
    lookup_field = "job_id"

    def get_queryset(self):
        job_id = self.kwargs.get("job_id")
        job = Jobs.objects.get(id=job_id)

        # Check permission
        self.check_object_permissions(self.request, job)

        return Applications.objects.filter(job=job).order_by('-applied_at')

class JobApplicationStatusUpdateView(generics.UpdateAPIView):
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
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notifications.objects.filter(recipient=self.request.user).order_by('is_read', '-created_at')


class NotificationDetailView(generics.RetrieveAPIView):
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
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Notifications.objects.filter(recipient=self.request.user)