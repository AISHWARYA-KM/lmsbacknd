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
    instructor = models.CharField(max_length=100)
    image = models.ImageField(upload_to='courses/', null=True, blank=True)
    description = models.TextField()
    thumbnail = CloudinaryField('thumbnail', null=True, blank=True)
    video_file = CloudinaryField('video', resource_type='video', null=True, blank=True)
    youtube_url = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, null=True, blank=True)
    referral_code = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.user.username

# New Model for User Course Enrollments
class UserCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrolled_users')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    phone= models.CharField(max_length=15, null=True, blank=True)
    referral_code = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"