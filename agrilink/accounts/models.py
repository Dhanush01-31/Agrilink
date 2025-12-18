from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    USER_TYPE_CHOICES = (
        ('farmer', 'Farmer'),
        ('landowner', 'Landowner'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.user.username


class FarmerDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_details')
    farmer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    experience_years = models.PositiveIntegerField()
    field_experience = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.farmer_name


class Land(models.Model):
    SOIL_CHOICES = (
        ('black', 'Black Soil'),
        ('red', 'Red Soil'),
        ('alluvial', 'Alluvial Soil'),
        ('sandy', 'Sandy Soil'),
    )

    SUITABLE_CHOICES = (
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('both', 'Both'),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lands')
    farm_name = models.CharField(max_length=200)
    soil_type = models.CharField(max_length=50, choices=SOIL_CHOICES)
    suitable_for = models.CharField(max_length=50, choices=SUITABLE_CHOICES)
    location = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.farm_name


class LandImage(models.Model):
    land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='land_photos/')

    def __str__(self):
        return f"Image for {self.land.farm_name}"


class LandRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )

    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='land_requests')
    land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name='requests')
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.farmer.username} → {self.land.farm_name}"
