# Generated by Django 3.1 on 2025-07-04 13:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('students', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HousingInspection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inspection_date', models.DateTimeField(auto_now_add=True, verbose_name='Tekshirish sanasi')),
                ('condition', models.CharField(choices=[('good', 'Yaxshi'), ('average', "O'rtacha"), ('poor', 'Yomon')], max_length=10, verbose_name='Holat')),
                ('comment', models.TextField(verbose_name='Izoh')),
                ('status', models.CharField(choices=[('pending', 'Kutilmoqda'), ('approved', 'Tasdiqlangan'), ('rejected', 'Rad etilgan')], default='pending', max_length=10, verbose_name='Status')),
                ('dean_comment', models.TextField(blank=True, verbose_name='Dekan izohi')),
                ('reviewed_at', models.DateTimeField(blank=True, null=True, verbose_name="Ko'rib chiqilgan sana")),
                ('cleanliness_score', models.IntegerField(default=5, help_text='1-10 ball', verbose_name='Tozalik darajasi')),
                ('safety_score', models.IntegerField(default=5, help_text='1-10 ball', verbose_name='Xavfsizlik darajasi')),
                ('comfort_score', models.IntegerField(default=5, help_text='1-10 ball', verbose_name='Qulaylik darajasi')),
                ('inspector', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inspections', to=settings.AUTH_USER_MODEL, verbose_name='Tekshiruvchi')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_inspections', to=settings.AUTH_USER_MODEL, verbose_name="Ko'rib chiquvchi")),
            ],
            options={
                'verbose_name': 'Yashash sharoiti tekshiruvi',
                'verbose_name_plural': 'Yashash sharoiti tekshiruvlari',
                'ordering': ['-inspection_date'],
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField(verbose_name="To'liq manzil")),
                ('room_number', models.CharField(blank=True, max_length=20, verbose_name='Xona raqami')),
                ('room_type', models.CharField(choices=[('single', 'Yakka xona'), ('double', 'Ikki kishilik'), ('shared', 'Umumiy xona')], max_length=10, verbose_name='Xona turi')),
                ('area', models.FloatField(help_text='Kvadrat metrda', verbose_name='Maydoni')),
                ('rent_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Ijara narxi')),
                ('has_kitchen', models.BooleanField(default=False, verbose_name='Oshxona bor')),
                ('has_bathroom', models.BooleanField(default=False, verbose_name='Hammom bor')),
                ('has_internet', models.BooleanField(default=False, verbose_name='Internet bor')),
                ('has_heating', models.BooleanField(default=False, verbose_name='Isitish tizimi')),
                ('condition', models.CharField(choices=[('excellent', "A'lo"), ('good', 'Yaxshi'), ('average', "O'rtacha"), ('poor', 'Yomon')], default='good', max_length=10, verbose_name='Umumiy holati')),
                ('landlord_name', models.CharField(max_length=100, verbose_name='Uy egasi ismi')),
                ('landlord_phone', models.CharField(max_length=20, verbose_name='Uy egasi telefoni')),
                ('notes', models.TextField(blank=True, verbose_name="Qo'shimcha ma'lumotlar")),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan sana')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yangilangan sana')),
            ],
            options={
                'verbose_name': 'Xona',
                'verbose_name_plural': 'Xonalar',
            },
        ),
        migrations.CreateModel(
            name='InspectionPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(upload_to='housing_photos/', verbose_name='Rasm')),
                ('caption', models.CharField(blank=True, max_length=100, verbose_name='Izoh')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Yuklangan sana')),
                ('inspection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='housing.housinginspection', verbose_name='Tekshirish')),
            ],
            options={
                'verbose_name': 'Tekshirish rasmi',
                'verbose_name_plural': 'Tekshirish rasmlari',
            },
        ),
        migrations.AddField(
            model_name='housinginspection',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inspections', to='housing.room', verbose_name='Xona'),
        ),
        migrations.AddField(
            model_name='housinginspection',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='housing_inspections', to='students.student', verbose_name='Talaba'),
        ),
    ]
