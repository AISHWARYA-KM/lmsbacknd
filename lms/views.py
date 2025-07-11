from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import Course, UserProfile, UserCourse
from .serializers import (
    RegisterSerializer,
    CourseSerializer,
    UserProfileSerializer,
    AdminUserSerializer,
    UserCourseSerializer,
    UserCourseDetailSerializer,
    CustomTokenObtainPairSerializer,
)

# ✅ Register API
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]  # Allow anyone to register
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


# ✅ Password Reset
class SimplePasswordResetView(APIView):
    def post(self, request):
        email = request.data.get("email")
        new_password = request.data.get("password")

        if not email or not new_password:
            return Response({"error": "Email and password are required."}, status=400)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "Email not registered."}, status=404)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password reset successful."})


# ✅ Course List API with filters
class CourseListAPIView(APIView):
    
    def get(self, request):
        courses = Course.objects.all()

        category = request.GET.getlist('category')
        level = request.GET.getlist('level')
        price_type = request.GET.getlist('price_type')
        instructor = request.GET.getlist('instructor')

        if category:
            courses = courses.filter(category__in=category)
        if level:
            courses = courses.filter(level__in=level)
        if price_type:
            courses = courses.filter(price_type__in=price_type)
        if instructor:
            courses = courses.filter(instructor__in=instructor)

        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


# ✅ Course Detail API by ID
class CourseDetailAPIView(RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


# ✅ Add Course (Admin Only) — FIXED ✅✅✅
class AddCourseAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # ⚠️ Required for file upload

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)

        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
# ✅ Admin - View All Courses (No filters, full access)
class AdminViewCoursesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)

        courses = Course.objects.filter(created_by=request.user)

        category = request.GET.getlist('category')
        level = request.GET.getlist('level')
        price_type = request.GET.getlist('price_type')
        instructor = request.GET.getlist('instructor')

        if category:
            courses = courses.filter(category__in=category)
        if level:
            courses = courses.filter(level__in=level)
        if price_type:
            courses = courses.filter(price_type__in=price_type)
        if instructor:
            courses = courses.filter(instructor__in=instructor)

        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

class ListRegisteredUsersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)

        users = User.objects.filter(is_superuser=False)
        serializer = AdminUserSerializer(users, many=True)
        return Response(serializer.data)

# ✅ Admin - Create User
class AssignedCoursesListAPIView(ListAPIView):
    serializer_class = UserCourseDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_superuser:
            return UserCourse.objects.none()  # Return empty queryset if not admin
        return UserCourse.objects.select_related('user', 'course')

    def list(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_create_user(request):
    if not request.user.is_superuser:
        return Response({'error': 'Permission denied'}, status=403)

    serializer = AdminUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

# ✅ Admin - Assign Course to User
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_course_to_user(request):
    if not request.user.is_superuser:
        return Response({'error': 'Permission denied'}, status=403)

    serializer = UserCourseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

# ✅ Get Logged-In User Profile Info
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found.'}, status=404)

    serializer = UserProfileSerializer(profile)
    return Response(serializer.data)


# ✅ Student - See Their Assigned Courses
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_assigned_courses(request):
    user = request.user
    assigned = UserCourse.objects.filter(user=user).select_related('course')

    class SimpleCourseSerializer(serializers.ModelSerializer):
        class Meta:
            model = Course
            fields = ['id', 'title', 'description', 'thumbnail_url', 'video_url', 'price', 'level', 'instructor']

    courses = [item.course for item in assigned]
    serializer = SimpleCourseSerializer(courses, many=True)
    return Response(serializer.data)

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'phone', 'referral_code']

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(id=user_id)
        if user.is_superuser:
            return Response({'error': 'Cannot delete superuser'}, status=400)

        user.delete()
        return Response({'message': 'User deleted successfully'}, status=200)

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
# ✅ Custom Login Token with extra user info
class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
