from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from .models import Course, UserProfile, UserCourse, OrganizationProfile, Batch, BatchCourse

# ✅ Register User Serializer
class RegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True, required=True)
    referral_code = serializers.CharField(write_only=True, required=False, allow_blank=True)
    role = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone', 'referral_code', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        phone = validated_data.pop('phone')
        referral_code = validated_data.pop('referral_code', '')
        role = validated_data.pop('role', 'student') 

        username = validated_data.get('username')
        email = validated_data.get('email')

        if User.objects.filter(username=username).exists():
            raise ValidationError({'username': 'Username already exists.'})
        if User.objects.filter(email=email).exists():
            raise ValidationError({'email': 'Email already exists.'})

        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, phone=phone, referral_code=referral_code, role=role)
        return user

# ✅ Login Token Serializer with Role and Email
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

        attrs['username'] = user.username
        self.user = user
        data = super().validate(attrs)

        data['user_id'] = user.id
        data['username'] = user.username
        data['email'] = user.email
        data['is_superuser'] = user.is_superuser

        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': 'student'})
        data['role'] = profile.role.lower()
        data['phone'] = profile.phone
        data['referral_code'] = profile.referral_code

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['is_superuser'] = user.is_superuser
        return token

# ✅ Admin/Org Create User Serializer
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
# ✅ Course Serializer
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

# ✅ Assign Courses to Users
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

# ✅ Admin View: Full Info of Assigned Courses
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
        fields = [
            'id', 'username', 'email', 'course_id', 'course_title',
            'enrolled_at', 'category', 'level', 'price', 'instructor', 'thumbnail_url'
        ]

    def get_thumbnail_url(self, obj):
        return obj.course.thumbnail_url if obj.course and obj.course.thumbnail else "/default-thumbnail.jpg"

# ✅ User Profile Serializer
class UserProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(read_only=True)
    referral_code = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'username': instance.user.username,
            'email': instance.user.email,
            'phone': instance.phone,
            'referral_code': instance.referral_code,
            'role': instance.role.lower()
        }

# ✅ Organization Profile Serializer
class OrganizationProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationProfile
        fields = ['id', 'user', 'organization_name']

# ✅ Batch Serializer
class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ['id', 'organization', 'name', 'users']
        extra_kwargs = {
            'organization': {'read_only': True},
            'users': {'required': False}
        }

# ✅ Batch Course Assignment Serializer
class BatchCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchCourse
        fields = ['id', 'batch', 'course']

# ✅ Simple User Serializer for Batch Assignment
class BatchUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class OrganizationCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'title', 'description', 'category', 'level', 'price_type', 'price',
            'old_price', 'instructor', 'image', 'thumbnail', 'video_file',
            'youtube_url', 'organization'
        ]
        extra_kwargs = {'organization': {'read_only': True}}

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username']