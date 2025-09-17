from django.db import models
from django.utils import timezone
from accounts.models import User
from students.models import Student
from faculty.models import Group
from datetime import date

class Attendance(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    taken_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_locked = models.BooleanField(default=False)  # Once locked, cannot be modified

    class Meta:
        unique_together = ['group', 'date']

    def __str__(self):
        return f"{self.group.name} - {self.date}"

    def save(self, *args, **kwargs):
        if self.pk:  # If updating existing record
            self.is_locked = True
        super().save(*args, **kwargs)

class AttendanceRecord(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    is_present = models.BooleanField(default=True)
    note = models.TextField(blank=True)

    class Meta:
        unique_together = ['attendance', 'student']

    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.student.full_name} - {status}"
