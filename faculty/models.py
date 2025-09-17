from django.db import models

# Create your models here.
from django.db import models


class Faculty(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    dean = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='dean_of',
        verbose_name="Dekan"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    
    class Meta:
        verbose_name = "Fakultet"
        verbose_name_plural = "Fakultetlar"
    
    def __str__(self):
        return self.name
    
    @property
    def groups_count(self):
        return self.groups.count()
    
    @property
    def students_count(self):
        return sum(group.students.count() for group in self.groups.all())


class Group(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nomi")
    faculty = models.ForeignKey(
        Faculty, 
        on_delete=models.CASCADE, 
        related_name='groups',
        verbose_name="Fakultet"
    )
    tutor = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_groups',
        verbose_name="Tutor"
    )
    course = models.IntegerField(default=1, verbose_name="Kurs")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    
    class Meta:
        verbose_name = "Guruh"
        verbose_name_plural = "Guruhlar"
        unique_together = ['name', 'faculty']
    
    def __str__(self):
        return f"{self.name} - {self.faculty.name}"
    
    @property
    def students_count(self):
        return self.students.count()
    
    @property
    def male_students_count(self):
        return self.students.filter(gender='male').count()
    
    @property
    def female_students_count(self):
        return self.students.filter(gender='female').count()
    
    @property
    def renting_students_count(self):
        return self.students.filter(is_renting=True).count()

    @property
    def dormitory_students_count(self):
        return self.students.filter(lives_in_dormitory=True).count()

    @property
    def disabled_students_count(self):
        return self.students.filter(has_disability=True).count()