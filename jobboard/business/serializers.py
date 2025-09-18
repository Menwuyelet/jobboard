from rest_framework import serializers
from django.db import transaction
from .models import Categories, Jobs, Applications, Notifications
from accounts.models import User 

class CategorySerializer(serializers.ModelSerializer):   
    jobs_count = serializers.IntegerField(source='jobs.count', read_only=True) 
    class Meta:
        model = Categories
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'jobs_count']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        if Categories.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A category with this name already exists.")
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        category = Categories.objects.create(**validated_data)
        return category
    
    @transaction.atomic
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class JobSerializer(serializers.ModelSerializer):
    posted_by = serializers.PrimaryKeyRelatedField(read_only=True)
    applications_count = serializers.IntegerField(source='applications.count', read_only=True)
    class Meta:
        model = Jobs
        fields = [
            'id', 'title', 'description', 'location',
            'working_area', 'longevity', 'type',
            'category', 'posted_by', 'posted_at', 'applications_count', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'posted_at', 'updated_at']

    def validate(self, data):
        if data.get("working_area") == "remote" and data.get("location"):
            raise serializers.ValidationError("Remote jobs should not include a physical location.")
        return data

    @transaction.atomic
    def create(self, validated_data):
        job = Jobs.objects.create(**validated_data)
        return job
    
    @transaction.atomic
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class ApplicationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Applications
        fields = ['id', 'job', 'user', 'status', 'resume', 'cover_letter', 'applied_at', 'updated_at']
        read_only_fields = ['id', 'status', 'applied_at', 'updated_at']

    def validate_job(self, job):
        user = self.context['request'].user
        if Applications.objects.filter(job=job, user=user).exists():
            raise serializers.ValidationError("You have already applied for this job.")
        return job
    
    @transaction.atomic
    def create(self, validated_data):
        job = Jobs.objects.create(**validated_data)
        return job
    
    @transaction.atomic
    def update(self, instance, validated_data):
        if instance.status != "pending":
            raise serializers.ValidationError(
                f"Cannot update this application because its status is '{instance.status}'."
            )
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return  instance

class NotificationSerializer(serializers.ModelSerializer):
    application = serializers.PrimaryKeyRelatedField(read_only=True)
    recipient = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Notifications
        fields = ['id', 'application', 'recipient', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']

    @transaction.atomic
    def create(self, validated_data):
        notification = Notifications.objects.create(**validated_data)
        return notification
    
    @transaction.atomic
    def update(self, instance, validated_data):
        instance.is_read = validated_data.get('is_read', instance.is_read)
        instance.save()
        return instance