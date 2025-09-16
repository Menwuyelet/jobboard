from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsAdmin, IsOwnerOfInstance
from .serializers import UserSerializer
from .models import User


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated, IsOwnerOfInstance | IsAdmin]
    lookup_field = 'id'

    def get_queryset(self):
        return User.objects.filter(role='user')

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(role='user')

class UsertListView(generics.ListAPIView):
    serializer_class = UserSerializer
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.filter(role='user')

class UserVerifyView(generics.UpdateAPIView):
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
    permission_classes = [IsAdmin]
    serializer_class = UserSerializer
    lookup_field = 'id'
    queryset = User.objects.filter(role='admin')

    def perform_create(self, serializer):
        role = "admin"
        serializer.save(role=role, can_post_ajob=True)
    
    def perform_destroy(self, instance):
        instance.delete()