from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import generics
from .models import Course
from .serializers import RegisterSerializer, CourseSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import RetrieveAPIView
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


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


class CourseListAPIView(APIView):
    def get(self, request):
        courses = Course.objects.all()

        category = request.GET.get('category')
        level = request.GET.get('level')
        price_type = request.GET.get('price_type')
        instructor = request.GET.get('instructor')

        if category:
            courses = courses.filter(category__iexact=category)
        if level:
            courses = courses.filter(level__iexact=level)
        if price_type:
            courses = courses.filter(price_type__iexact=price_type)
        if instructor:
            courses = courses.filter(instructor__iexact=instructor)

        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
class CourseDetailAPIView(RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer