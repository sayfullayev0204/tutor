from django.db import models
from django.core.exceptions import ValidationError

CONDITION_CHOICES = (
        ('excellent', 'A\'lo'),
        ('good', 'Yaxshi'),
        ('average', 'O\'rtacha'),
        ('poor', 'Yomon'),
    )

class Mutaxassislik(models.Model):
    name = models.CharField(max_length=200, verbose_name="Mutaxassislik nomi")
    
    class Meta:
        verbose_name = "Mutaxassislik"
        verbose_name_plural = "Mutaxassisliklar"
    
    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=100, verbose_name="Davlat")
    
    class Meta:
        verbose_name = "Davlat"
        verbose_name_plural = "Davlatlar"
    
    def __str__(self):
        return self.name

class Region(models.Model):
    name = models.CharField(max_length=200, verbose_name="Viloyat")
    
    class Meta:
        verbose_name = "Viloyat"
        verbose_name_plural = "Viloyatlar"
    
    def __str__(self):
        return self.name

class District(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name="Viloyat")
    name = models.CharField(max_length=200, verbose_name="Tuman")
    
    class Meta:
        verbose_name = "Tuman"
        verbose_name_plural = "Tumanlar"
    
    def __str__(self):
        return self.name

class TTJ(models.Model):
    name = models.CharField(max_length=100, verbose_name="TTJ nomi")
    address = models.TextField(verbose_name="To'liq manzil")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name="Viloyat")
    district = models.ForeignKey(District, on_delete=models.CASCADE, verbose_name="Tuman")
    capacity = models.PositiveIntegerField(verbose_name="Sig'imi (kishi)")
    has_internet = models.BooleanField(default=False, verbose_name="Internet bor")
    has_heating = models.BooleanField(default=False, verbose_name="Isitish tizimi")
    condition = models.CharField(
        max_length=10,
        choices=CONDITION_CHOICES,  # Reusing choices from Room
        default='good',
        verbose_name="Umumiy holati"
    )
    manager_name = models.CharField(max_length=100, verbose_name="TTJ boshqaruvchisi ismi")
    manager_phone = models.CharField(max_length=20, verbose_name="TTJ boshqaruvchisi telefoni")
    notes = models.TextField(blank=True, verbose_name="Qo'shimcha ma'lumotlar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")
    
    class Meta:
        verbose_name = "Talabalar turar joyi (TTJ)"
        verbose_name_plural = "Talabalar turar joylari (TTJ)"
    
    def __str__(self):
        return f"{self.name} - {self.address}"

class Student(models.Model):
    GENDER_CHOICES = (
        ('male', 'Erkak'),
        ('female', 'Ayol'),
    )
    FUQARO_CHOICES = (
        ('uz', 'O‘zbekiston fuqarosi'),
        ('foreign', 'Chet el fuqarosi'),
    )
    TALIM_CHOICES = (
        ('bakalavr', 'Bakalavr'),
        ('magistr', 'Magistr'),
        ('doktorant', 'Doktorant'),
        ('phd', 'PhD'),
    )
    TULOV_CHOICES = (
        ('grant', 'Davlat granti'),
        ('contract', 'To‘lov-kontrakt'),
    )
    TALIM_SHAKLI_CHOICES = (
        ('kunduzgi', 'Kunduzgi'),
        ('sirtqi', 'Sirtqi'),
        ('kechki', 'Kechki'),
        ('masofaviy', 'Masofaviy'),
    )
    COURSE_CHOICES = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
    )
    APPARTMENT_TYPE_CHOICES = (
        ('ttj', 'TTJ (Talabalar turar joyi)'),
        ('rent', 'Ijara xonadon'),
        ('home', 'Uyda yashaydi'),
    )
    FAMILY_CHOICES = (
        ('turmush_qurgan', 'Turmush qurgan'),
        ('turmush_qurmagan', 'Turmush qurgan emas'),
    )
    
    first_name = models.CharField(max_length=50, verbose_name="Ism")
    last_name = models.CharField(max_length=50, verbose_name="Familiya")
    middle_name = models.CharField(max_length=50, blank=True, verbose_name="Otasining ismi")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Jinsi")
    birth_date = models.DateField(verbose_name="Tug'ilgan sana")
    group = models.ForeignKey(
        'faculty.Group', 
        on_delete=models.CASCADE, 
        related_name='students',
        verbose_name="Guruh"
    )
    is_renting = models.BooleanField(default=False, verbose_name="Ijara xonadonida yashaydi")
    address = models.TextField(blank=True, verbose_name="Manzil")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Telefon raqami")
    email = models.EmailField(blank=True, verbose_name="Email")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    
    # Additional fields for special categories
    is_orphan = models.BooleanField(default=False, verbose_name="Yetim")
    has_disability = models.BooleanField(default=False, verbose_name="Nogironligi bor")
    lives_in_dormitory = models.BooleanField(default=False, verbose_name="TTJ da yashaydi")
    
    # Personal information
    student_id = models.IntegerField(verbose_name="Talaba ID", unique=True, default=0)
    fuqaro = models.CharField(max_length=20, choices=FUQARO_CHOICES, default='uz', verbose_name="Fuqarolik")
    jshshir = models.CharField(max_length=14, verbose_name="JSHSHIR raqami", unique=True)  # Changed to CharField for JSHSHIR
    passport = models.CharField(max_length=20, verbose_name="Pasport raqami", unique=True)
    otm = models.CharField(max_length=100, verbose_name="Oliy ta'lim muassasasi")
    talim_turi = models.CharField(max_length=20, choices=TALIM_CHOICES, default='bakalavr', verbose_name="Ta'lim turi")
    tulov_turi = models.CharField(max_length=20, choices=TULOV_CHOICES, default='grant', verbose_name="To'lov turi")
    talim_shakli = models.CharField(max_length=20, choices=TALIM_SHAKLI_CHOICES, default='kunduzgi', verbose_name="Ta'lim shakli")
    shifr = models.CharField(max_length=20, verbose_name="Shifr")  # Changed to CharField for flexibility
    mutaxassislik = models.ForeignKey(Mutaxassislik, on_delete=models.CASCADE, verbose_name="Mutaxassislik")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name="Vatan")
    const_region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='const_students', verbose_name="Doimiy viloyat")
    const_district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='const_students', verbose_name="Doimiy tuman")
    temporary_region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='temp_students', verbose_name="Vaqtincha viloyat")
    temporary_district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='temp_students', verbose_name="Vaqtincha tuman")
    temporary_address = models.TextField(blank=True, verbose_name="Yashash manzili")
    appartment_type = models.CharField(max_length=20, choices=APPARTMENT_TYPE_CHOICES, default='ttj', verbose_name="Yashash turi")
    family_type = models.CharField(max_length=20, choices=FAMILY_CHOICES, default='turmush_qurmagan', verbose_name="Oilaviy holati")
    bully_student = models.BooleanField(default=False, verbose_name="Bezori talaba")
    # Conditional ForeignKeys
    room = models.ForeignKey(
        'housing.Room',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name="Ijara xona"
    )
    ttj = models.ForeignKey(
        TTJ,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name="TTJ"
    )
    
    class Meta:
        verbose_name = "Talaba"
        verbose_name_plural = "Talabalar"
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
    
    def clean(self):
        # Validation for conditional ForeignKeys
        if self.appartment_type == 'rent' and not self.room:
            raise ValidationError("Ijara xonadon tanlanganda 'room' maydoni to'ldirilishi kerak.")
        if self.appartment_type == 'ttj' and not self.ttj:
            raise ValidationError("TTJ tanlanganda 'ttj' maydoni to'ldirilishi kerak.")
        if self.appartment_type == 'home' and (self.room or self.ttj):
            raise ValidationError("'Uyda yashaydi' tanlanganda 'room' yoki 'ttj' maydonlari bo'sh bo'lishi kerak.")
        if self.appartment_type != 'rent' and self.room:
            raise ValidationError("Faqat 'Ijara xonadon' tanlanganda 'room' maydoni to'ldirilishi mumkin.")
        if self.appartment_type != 'ttj' and self.ttj:
            raise ValidationError("Faqat 'TTJ' tanlanganda 'ttj' maydoni to'ldirilishi mumkin.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

        