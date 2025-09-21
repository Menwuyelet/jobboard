from rest_framework import serializers
from .models import User
from django.db import transaction
import re
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the custom User model.

    Handles user creation, update, and password validation.
    - Password is write-only and validated for complexity.
    - Role is read-only and cannot be modified via this serializer.
    - Certain fields like can_post_ajob, jobs_posted, and number_of_hires are read-only.
    """    
    password = serializers.CharField(required=True, write_only=True)
    role = serializers.CharField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name', 'can_post_ajob', 'jobs_posted', 'number_of_hires', 'gender', 'nationality', 'password']
        read_only_fields = ['id', 'can_post_ajob', 'jobs_posted', 'number_of_hires',]

    def validate_password(self, value):
        """
        Validate password complexity.

        Ensures password contains:
        - At least one letter
        - At least one number
        - At least one special character
        """
        validate_password(value)

        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("Password must contain at least one letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number.")
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")

        return value

    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new User instance.
        """
        user_name = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        if not email:
            raise serializers.ValidationError("Email must be provided.")
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email must be unique. choose another one.")
        
        if not user_name:
            raise serializers.ValidationError("user Name must be provided.")
        if User.objects.filter(username=user_name).exists():
            raise serializers.ValidationError("User name must be unique. choose another one.")
        
        user = User.objects.create(email=email, username=user_name, **validated_data)
        user.set_password(password)
        user.save()
        return user


    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Update an existing User instance.
        """
        user_name = validated_data.pop('username', None)
        email = validated_data.pop('email', None)
        password = validated_data.pop('password', None)

        if email and User.objects.filter(email=email).exclude(id=instance.id).exists():
            raise serializers.ValidationError("Email must be unique. Choose another one.")
        if user_name and User.objects.filter(username=user_name).exclude(id=instance.id).exists():
            raise serializers.ValidationError("Username must be unique. Choose another one.")

        if password:
            instance.set_password(password)


        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
