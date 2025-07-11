from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from .models import Course, UserProfile, UserCourse

# ✅ User Registration Serializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import UserProfile

class RegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True, required=True)
    referral_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone', 'referral_code']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        phone = validated_data.pop('phone')
        referral_code = validated_data.pop('referral_code', '')

        username = validated_data.get('username')
        email = validated_data.get('email')

        if User.objects.filter(username=username).exists():
            raise ValidationError({'username': 'Username already exists.'})
        if User.objects.filter(email=email).exists():
            raise ValidationError({'email': 'Email already exists.'})

        # Create the user
        user = User.objects.create_user(**validated_data)

        # Create the profile with phone and referral
        UserProfile.objects.create(user=user, phone=phone, referral_code=referral_code)

        return user

# ✅ Course Serializer (with thumbnail and video URL support)
class CourseSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_thumbnail_url(self, obj):
        return obj.thumbnail_url

    def get_video_url(self, obj):
        return obj.video_url

# ✅ Login with Email/Password Token Serializer
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].required = False

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise AuthenticationFailed('Email and password are required.')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed('User with this email not found.')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password.')

        self.user = user
        attrs['username'] = user.username
        data = super().validate(attrs)

        data["is_superuser"] = user.is_superuser
        data["user_id"] = user.id
        data["username"] = user.username
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["is_superuser"] = user.is_superuser
        return token

# ✅ Admin Create User
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user)
        return user

# ✅ Assign Courses to Users (Short Serializer)
class UserCourseSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = UserCourse
        fields = ['id', 'user', 'course', 'user_username', 'course_title']
        extra_kwargs = {
            'user': {'write_only': True},
            'course': {'write_only': True},
        }

    def validate(self, data):
        if UserCourse.objects.filter(user=data['user'], course=data['course']).exists():
            raise serializers.ValidationError("User is already enrolled in this course.")
        return data

# ✅ Admin View: Assigned Course Detail with Full Info
class UserCourseDetailSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    category = serializers.CharField(source='course.category', read_only=True)
    level = serializers.CharField(source='course.level', read_only=True)
    price = serializers.DecimalField(source='course.price', max_digits=6, decimal_places=2, read_only=True)
    instructor = serializers.CharField(source='course.instructor', read_only=True)
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = UserCourse
        fields = ['id', 'username', 'email', 'course_id', 'course_title', 'enrolled_at','category', 'level', 'price', 'instructor', 'thumbnail_url']
    def get_thumbnail_url(self, obj):
        return obj.course.thumbnail_url if obj.course and obj.course.thumbnail else "/default-thumbnail.jpg"   
# ✅ UserProfile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'phone', 'referral_code']
