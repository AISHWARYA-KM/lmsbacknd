from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Course(models.Model):
    CATEGORY_CHOICES = [
        ('Manual Testing', 'Manual Testing'),
        ('Automation Testing', 'Automation Testing'),
        ('API Testing', 'API Testing'),
        ('Mobile Testing', 'Mobile Testing'),
        ('Python Development', 'Python Development'),
        ('java Development', 'java Development'),
        ('UI/UX', 'UI/UX'),
        ('mern Stack', 'mern Stack'),
    ]

    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advance', 'Advance'),
    ]

    PRICE_TYPE = [
        ('Free', 'Free'),
        ('Paid', 'Paid'),
    ]

    INSTRUCTOR_CHOICES = [
        ('Pramod', 'Pramod'),
        ('Mani', 'Mani'),
        ('Bharat', 'Bharat'),
        ('Kartik', 'Bob Brown'),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES)
    price_type = models.CharField(max_length=10, choices=PRICE_TYPE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    old_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    students = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    instructor = models.CharField(max_length=100, choices=INSTRUCTOR_CHOICES)
    image = models.ImageField(upload_to='courses/', null=True, blank=True)
    description = models.TextField()
    thumbnail = CloudinaryField('thumbnail', null=True, blank=True)
    video_file = CloudinaryField('video', resource_type='video', null=True, blank=True)
    youtube_url = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_courses')
    organization = models.ForeignKey('OrganizationProfile', on_delete=models.CASCADE, null=True, blank=True)

    @property
    def thumbnail_url(self):
        return self.thumbnail.url if self.thumbnail else "/default-thumbnail.jpg"

    @property
    def video_url(self):
        if self.video_file:
            return self.video_file.url
        elif self.youtube_url:
            return self.youtube_url
        return None

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('organization', 'Organization'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, null=True, blank=True)
    referral_code = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} [{self.role}]"


class UserCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrolled_users')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    referral_code = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"


class OrganizationProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=255)

    def __str__(self):
        return self.organization_name


class Batch(models.Model):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(OrganizationProfile, on_delete=models.CASCADE, related_name='batches')
    users = models.ManyToManyField(User, related_name='batches', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    courses = models.ManyToManyField(Course, related_name='batches')


    def __str__(self):
        return f"{self.name} ({self.organization.organization_name})"


class BatchCourse(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='assigned_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('batch', 'course')

    def __str__(self):
        return f"{self.course.title} to {self.batch.name}"
