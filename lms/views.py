from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from .models import Course, UserProfile, UserCourse, Batch, BatchCourse, OrganizationProfile
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import (
    RegisterSerializer,
    CourseSerializer,
    UserProfileSerializer,
    AdminUserSerializer,
    UserCourseSerializer,
    UserCourseDetailSerializer,
    CustomTokenObtainPairSerializer,
    BatchSerializer,UserSerializer
)

# ✅ Register API
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
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


# ✅ Add Course (Admin Only)
class AddCourseAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)

        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# ✅ Admin - View All Courses
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


# ✅ Admin - Assigned Course Detail
class AssignedCoursesListAPIView(ListAPIView):
    serializer_class = UserCourseDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_superuser:
            return UserCourse.objects.none()
        return UserCourse.objects.select_related('user', 'course')


# ✅ Admin - Create User


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_create_user(request):
    serializer = AdminUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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


# ✅ Get Logged-In User Profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    if not profile:
        return Response({'error': 'User profile not found.'}, status=404)

    serializer = UserProfileSerializer(profile)
    return Response(serializer.data)


# ✅ Student - View Assigned Courses
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


# ✅ Delete User
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return Response({'error': 'Permission denied'}, status=403)

    try:
        user = User.objects.get(id=user_id)
        if user.is_superuser:
            return Response({'error': 'Cannot delete superuser'}, status=400)

        user.delete()
        return Response({'message': 'User deleted successfully'}, status=200)

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


# ✅ Login with Role Data
class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ✅ Organization Add Course s
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def org_view_users(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    if not profile or profile.role.lower() != "organization":
        return Response({'error': 'Only organization users can view users'}, status=403)

    users = User.objects.filter(is_superuser=False)
    serializer = AdminUserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def org_view_courses(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    if not profile or profile.role.lower() != "organization":
        return Response({'error': 'Only organization users can view courses'}, status=403)

    courses = Course.objects.all()
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_or_org_create_user(request):
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=403)

    if not user.is_superuser and profile.role != 'organization':
        return Response({'error': 'Permission denied'}, status=403)

    serializer = AdminUserSerializer(data=request.data)
    if serializer.is_valid():
        created_user = serializer.save()

        # Assign role if organization creates the user
        if profile.role == 'organization':
            created_profile, _ = UserProfile.objects.get_or_create(user=created_user)
            created_profile.created_by = user
            created_profile.role = 'student'  # or any default you want
            created_profile.save()

        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)




class CreateBatchView(generics.CreateAPIView):
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        profile = UserProfile.objects.filter(user=request.user).first()
        if not profile or profile.role.lower() != "organization":
            return Response({'error': 'Only organization users can create batches'}, status=403)

        org_profile = OrganizationProfile.objects.filter(user=request.user).first()
        if not org_profile:
            return Response({'error': 'Organization profile not found'}, status=404)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organization=org_profile)
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)  # 👈 This shows the exact validation errors

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_batches_for_org(request):
    user = request.user
    try:
        org = OrganizationProfile.objects.get(user=user)
    except OrganizationProfile.DoesNotExist:
        return Response({"error": "Organization not found."}, status=404)

    batches = Batch.objects.filter(organization=org)
    data = [{"id": batch.id, "name": batch.name} for batch in batches]
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_course_to_batch(request, batch_id):
    profile = UserProfile.objects.filter(user=request.user).first()
    if not profile or profile.role.lower() != "organization":
        return Response({'error': 'Only organization users can assign courses to batches'}, status=403)

    try:
        batch = Batch.objects.get(id=batch_id)
    except Batch.DoesNotExist:
        return Response({'error': 'Batch not found'}, status=404)

    course_id = request.data.get('course_id')
    if not course_id:
        return Response({'error': 'Course ID is required'}, status=400)

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=404)

    # Check if the course is already assigned
    if BatchCourse.objects.filter(batch=batch, course=course).exists():
        return Response({'message': 'Course already assigned to batch'}, status=200)

    # Create the assignment
    BatchCourse.objects.create(batch=batch, course=course)
    return Response({'message': 'Course assigned to batch successfully'}, status=201)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def non_admin_users(request):
    users = User.objects.filter(is_superuser=False)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

# ✅ Assign Existing User to Batch (organization-only)},
class AddUserToBatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, batch_id):
        user_id = request.data.get("user_id")

        if not user_id:
            return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            batch = Batch.objects.get(id=batch_id)
        except Batch.DoesNotExist:
            return Response({"error": "Batch not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Add user to the batch
        batch.users.add(user)
        return Response({"message": "User assigned to batch successfully."}, status=status.HTTP_200_OK)
class ListBatchCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, batch_id):
        # Check if the user is an organization
        profile = UserProfile.objects.filter(user=request.user).first()
        if not profile or profile.role.lower() != "organization":
            return Response({'error': 'Only organization users can view batch courses'}, status=403)

        try:
            batch = Batch.objects.get(id=batch_id)
        except Batch.DoesNotExist:
            return Response({'error': 'Batch not found'}, status=404)

        batch_courses = BatchCourse.objects.filter(batch=batch).select_related('course')
        courses = [bc.course for bc in batch_courses]

        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_users_in_batch(request, batch_id):
    profile = UserProfile.objects.filter(user=request.user).first()
    if not profile or profile.role.lower() != "organization":
        return Response({'error': 'Only organization users can view users in a batch'}, status=403)

    try:
        batch = Batch.objects.get(id=batch_id)
        users = batch.users.all()
        data = [
            {"id": user.id, "username": user.username, "email": user.email}
            for user in users
        ]
        return Response(data)
    except Batch.DoesNotExist:
        return Response({"error": "Batch not found."}, status=404)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_course_by_name(request):
    try:
        batch_id = request.data.get('batch_id')
        course_title = request.data.get('course_title')

        # Directly find the BatchCourse using title and batch
        batch_course = BatchCourse.objects.select_related('course', 'batch').filter(
            batch__id=batch_id,
            course__title=course_title
        ).first()

        if not batch_course:
            return Response({'error': 'Course not assigned to this batch.'}, status=status.HTTP_404_NOT_FOUND)

        batch_course.delete()
        return Response({'message': 'Course removed from batch.'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_user_from_batch(request, batch_id, username):
    profile = UserProfile.objects.filter(user=request.user).first()
    if not profile or profile.role.lower() != "organization":
        return Response({'error': 'Only organization users can remove users from batches'}, status=403)

    try:
        batch = Batch.objects.get(id=batch_id)
    except Batch.DoesNotExist:
        return Response({'error': 'Batch not found'}, status=404)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    if user not in batch.users.all():
        return Response({'error': 'User is not part of this batch'}, status=400)

    batch.users.remove(user)
    return Response({'message': 'User removed from batch successfully'}, status=200)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_organization_user(request):
    data = request.data

    required_fields = ['username', 'email', 'password', 'phone', 'organization_name']
    missing_fields = [field for field in required_fields if not data.get(field)]

    if missing_fields:
        return Response({
            'error': f"Missing required fields: {', '.join(missing_fields)}"
        }, status=status.HTTP_400_BAD_REQUEST)

    username = data['username']
    email = data['email']
    password = data['password']
    phone = data['phone']
    organization_name = data['organization_name']
    referral_code = data.get('referral_code', '')

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    # Create the user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    # Create the user profile with role = 'organization'
    UserProfile.objects.create(
        user=user,
        phone=phone,
        referral_code=referral_code,
        role='organization'
    )

    # Create the organization profile
    OrganizationProfile.objects.create(
        user=user,
        organization_name=organization_name
    )

    return Response({
        'message': 'Organization user created successfully!',
        'user_id': user.id
    }, status=status.HTTP_201_CREATED)

class OrganizationProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if hasattr(user, 'organization_profile'):
            profile = user.organization_profile
            return Response({
                'id': profile.id,
                'name': profile.name,
                'email': user.email,
                'user_id': user.id,
            })
        return Response({'error': 'User has no organization profile'}, status=404)

class OrganizationAddCourseView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        profile = UserProfile.objects.filter(user=request.user).first()
        if not profile or profile.role != "organization":
            return Response({'error': 'Permission denied'}, status=403)

        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_batches_with_users(request):
    batches = Batch.objects.filter(organization=request.user.organizationprofile)
    data = []
    for batch in batches:
        users = batch.users.all()
        data.append({
            'id': batch.id,
            'name': batch.name,
            'users': UserSerializer(users, many=True).data
        })
    return Response(data)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_batches_with_courses(request):
    batches = Batch.objects.all()
    data = []

    for batch in batches:
        # Query the assigned courses via BatchCourse
        assigned_courses = BatchCourse.objects.filter(batch=batch).select_related('course')

        course_data = [
            {
                'id': bc.course.id,
                'title': bc.course.title,
                'description': bc.course.description,
            }
            for bc in assigned_courses
        ]

        data.append({
            'id': batch.id,
            'name': batch.name,
            'courses': course_data
        })

    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_batch_courses(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    if not profile or profile.role.lower() != "organization":
        return Response({'error': 'Only organization users can view batch courses'}, status=403)

    assignments = BatchCourse.objects.select_related('batch', 'course').all()

    data = [
        {
            'batch_id': bc.batch.id,
            'batch_name': bc.batch.name,
            'course_title': bc.course.title,
        }
        for bc in assignments
    ]
    return Response(data, status=200)















