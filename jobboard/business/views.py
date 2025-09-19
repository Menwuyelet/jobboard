from django.shortcuts import render
from .serializers import CategorySerializer, JobSerializer
from rest_framework import generics, viewsets
from accounts.permissions import IsAdmin, CanPost, IsOwnerOfInstance
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Categories, Jobs

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

    def get_permissions(self):
        if self.action == "create":
            # return [AllowAny()]  
            return [IsAuthenticated(), CanPost()]
        return [IsAuthenticated(), IsOwnerOfInstance()]

    def get_queryset(self):
        user = self.request.user
        return Jobs.objects.filter(posted_by=user).order_by('posted_at', 'is_active')

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
        queryset = Jobs.objects.all().order_by('posted_at', 'is_active')
        lookup_field = "id"
