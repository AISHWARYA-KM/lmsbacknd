from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Course

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class CourseSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'  # This will include DB fields + method fields
   
    def get_thumbnail_url(self, obj):
        return obj.thumbnail_url  # from your @property on model
    
    def get_video_url(self, obj):
        return obj.video_url  # from your @property on model


