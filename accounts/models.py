from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('rector', 'Rektor'),
        ('dean', 'Dekan'),
        ('tutor', 'Tutor'),
    )
    
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES,
        verbose_name="Foydalanuvchi turi"
    )
    faculty = models.ForeignKey(
        'faculty.Faculty', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Fakultet"
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        null=True, 
        blank=True,
        verbose_name="Profil rasmi"
    )
    phone_number = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name="Telefon raqami"
    )
    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
    
    def is_rector(self):
        return self.user_type == 'rector'
    
    def is_dean(self):
        return self.user_type == 'dean'
    
    def is_tutor(self):
        return self.user_type == 'tutor'
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    def get_assigned_group(self):
            # Replace with actual logic to get the tutor's group, e.g., via a related model
            # Example placeholder: return first group in the tutor's faculty
            from faculty.models import Group
            return Group.objects.filter(faculty=self.faculty).first()