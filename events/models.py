from django.db import models
from django.utils import timezone
from accounts.models import User

class Event(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('approved', 'Tasdiqlangan'),
        ('rejected', 'Rad etilgan'),
    )
    
    CATEGORY_CHOICES = (
        ('educational', 'Ta\'limiy'),
        ('cultural', 'Madaniy'),
        ('sports', 'Sport'),
        ('social', 'Ijtimoiy'),
        ('other', 'Boshqa'),
    )
    
    title = models.CharField(max_length=200, verbose_name="Tadbir nomi")
    description = models.TextField(verbose_name="Tadbir haqida")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Kategoriya")
    event_date = models.DateTimeField(verbose_name="Tadbir sanasi")
    location = models.CharField(max_length=200, verbose_name="O'tkazilgan joy")
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events',
        verbose_name="Tashkilotchi (Tutor)"
    )
    participants_count = models.PositiveIntegerField(verbose_name="Ishtirokchilar soni")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    
    # Tasdiqlash ma'lumotlari
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_events',
        verbose_name="Ko'rib chiquvchi"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Ko'rib chiqilgan sana")
    dean_comment = models.TextField(blank=True, verbose_name="Dekan izohi")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")
    
    class Meta:
        verbose_name = "Tadbir"
        verbose_name_plural = "Tadbirlar"
        ordering = ['-event_date']
    
    def __str__(self):
        return f"{self.title} - {self.event_date.strftime('%Y-%m-%d')}"

class EventPhoto(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name="Tadbir"
    )
    photo = models.ImageField(upload_to='event_photos/', verbose_name="Rasm")
    caption = models.CharField(max_length=200, blank=True, verbose_name="Rasm izohi")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuklangan sana")
    
    class Meta:
        verbose_name = "Tadbir rasmi"
        verbose_name_plural = "Tadbir rasmlari"
    
    def __str__(self):
        return f"{self.event.title} - Rasm"
