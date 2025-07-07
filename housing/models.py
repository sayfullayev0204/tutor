from django.db import models
from django.utils import timezone
from datetime import timedelta
from students.models import Student

class Room(models.Model):
    ROOM_TYPE_CHOICES = (
        ('single', 'Yakka xona'),
        ('double', 'Ikki kishilik'),
        ('shared', 'Umumiy xona'),
    )
        
    CONDITION_CHOICES = (
        ('excellent', 'A\'lo'),
        ('good', 'Yaxshi'),
        ('average', 'O\'rtacha'),
        ('poor', 'Yomon'),
    )
        
    address = models.TextField(verbose_name="To'liq manzil")
    room_number = models.CharField(max_length=20, blank=True, verbose_name="Xona raqami")
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, verbose_name="Xona turi")
    area = models.FloatField(help_text="Kvadrat metrda", verbose_name="Maydoni")
    rent_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ijara narxi")
    has_kitchen = models.BooleanField(default=False, verbose_name="Oshxona bor")
    has_bathroom = models.BooleanField(default=False, verbose_name="Hammom bor")
    has_internet = models.BooleanField(default=False, verbose_name="Internet bor")
    has_heating = models.BooleanField(default=False, verbose_name="Isitish tizimi")
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='good', verbose_name="Umumiy holati")
    landlord_name = models.CharField(max_length=100, verbose_name="Uy egasi ismi")
    landlord_phone = models.CharField(max_length=20, verbose_name="Uy egasi telefoni")
    notes = models.TextField(blank=True, verbose_name="Qo'shimcha ma'lumotlar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True) 
    class Meta:
        verbose_name = "Xona"
        verbose_name_plural = "Xonalar"
        
    def __str__(self):
        return f"{self.address} - {self.get_room_type_display()}"
        
    @property
    def current_residents(self):
        from students.models import Student
        return Student.objects.filter(is_renting=True, room=self)
    
    @property
    def inspection_status(self):
        """Xonaning tekshiruv statusini qaytaradi"""
        # Faqat tasdiqlangan tekshiruvlarni hisobga olish
        last_approved_inspection = self.inspections.filter(
            status='approved'
        ).order_by('-inspection_date').first()
        
        if not last_approved_inspection:
            return 'not_inspected'
        
        # Oxirgi tasdiqlangan tekshiruvdan necha kun o'tganini hisoblash
        days_since = (timezone.now().date() - last_approved_inspection.inspection_date.date()).days
        
        if days_since <= 30:
            return 'inspected'
        else:
            return 'overdue'
    
    @property
    def inspection_badge(self):
        """Status uchun badge ma'lumotlarini qaytaradi"""
        status = self.inspection_status
        badges = {
            'not_inspected': ('warning', 'Tekshirilmagan'),
            'inspected': ('success', 'Tekshirilgan'),
            'overdue': ('danger', 'Muddati o\'tgan'),
        }
        return badges.get(status, ('secondary', 'Noma\'lum'))
    
    @property
    def last_approved_inspection(self):
        """Oxirgi tasdiqlangan tekshiruvni qaytaradi"""
        return self.inspections.filter(status='approved').order_by('-inspection_date').first()
    
    @property
    def pending_inspections_count(self):
        """Kutilayotgan tekshiruvlar sonini qaytaradi"""
        return self.inspections.filter(status='pending').count()

class HousingInspection(models.Model):
    CONDITION_CHOICES = (
        ('good', 'Yaxshi'),
        ('average', 'O\'rtacha'),
        ('poor', 'Yomon'),
    )
        
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('approved', 'Tasdiqlangan'),
        ('rejected', 'Rad etilgan'),
    )
        
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='housing_inspections',
        verbose_name="Talaba"
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inspections',
        verbose_name="Xona"
    )
    inspector = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='inspections',
        verbose_name="Tekshiruvchi"
    )
    inspection_date = models.DateTimeField(auto_now_add=True, verbose_name="Tekshirish sanasi")
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, verbose_name="Holat")
    comment = models.TextField(verbose_name="Izoh")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    dean_comment = models.TextField(blank=True, verbose_name="Dekan izohi")
    reviewed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_inspections',
        verbose_name="Ko'rib chiquvchi"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Ko'rib chiqilgan sana")
        
    # Additional inspection details
    cleanliness_score = models.IntegerField(default=5, help_text="1-10 ball", verbose_name="Tozalik darajasi")
    safety_score = models.IntegerField(default=5, help_text="1-10 ball", verbose_name="Xavfsizlik darajasi")
    comfort_score = models.IntegerField(default=5, help_text="1-10 ball", verbose_name="Qulaylik darajasi")
        
    class Meta:
        verbose_name = "Yashash sharoiti tekshiruvi"
        verbose_name_plural = "Yashash sharoiti tekshiruvlari"
        ordering = ['-inspection_date']
        
    def __str__(self):
        return f"{self.student.full_name} uchun tekshirish - {self.inspection_date.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        # Automatically set inspection date if not provided
        if not self.inspection_date:
            self.inspection_date = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def overall_score(self):
        return round((self.cleanliness_score + self.safety_score + self.comfort_score) / 3, 1)

class InspectionPhoto(models.Model):
    inspection = models.ForeignKey(
        HousingInspection,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name="Tekshirish"
    )
    photo = models.ImageField(upload_to='housing_photos/', verbose_name="Rasm")
    caption = models.CharField(max_length=100, blank=True, verbose_name="Izoh")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuklangan sana")
        
    class Meta:
        verbose_name = "Tekshirish rasmi"
        verbose_name_plural = "Tekshirish rasmlari"
        
    def __str__(self):
        return f"{self.inspection.student.full_name} - Rasm"
