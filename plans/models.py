from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Plan(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Past'),
        ('medium', 'O\'rtacha'),
        ('high', 'Yuqori'),
        ('urgent', 'Shoshilinch'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('in_progress', 'Jarayonda'),
        ('completed', 'Bajarildi'),
        ('cancelled', 'Bekor qilindi'),
    )
    
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    description = models.TextField(verbose_name="Tavsif")
    tutor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='plans',
        verbose_name="Tutor"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="Muhimlik darajasi"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Holat"
    )
    due_date = models.DateTimeField(verbose_name="Bajarish muddati")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Bajarilgan sana")
    
    class Meta:
        verbose_name = "Reja"
        verbose_name_plural = "Rejalar"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now() and self.status != 'completed'


class Reminder(models.Model):
    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name='reminders',
        verbose_name="Reja"
    )
    title = models.CharField(max_length=200, verbose_name="Eslatma sarlavhasi")
    message = models.TextField(verbose_name="Eslatma matni")
    remind_at = models.DateTimeField(verbose_name="Eslatish vaqti")
    is_sent = models.BooleanField(default=False, verbose_name="Yuborilganmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    
    class Meta:
        verbose_name = "Eslatma"
        verbose_name_plural = "Eslatmalar"
        ordering = ['remind_at']
    
    def __str__(self):
        return f"{self.title} - {self.remind_at.strftime('%Y-%m-%d %H:%M')}"
