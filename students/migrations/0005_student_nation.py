# Generated by Django 5.2.4 on 2025-07-16 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_student_is_in_orphanage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='nation',
            field=models.CharField(choices=[('uzbek', "O'zbek"), ('russian', 'Rus'), ('tajik', 'Tojik'), ('kazakh', 'Qozoq'), ('kyrgyz', "Qirg'iz"), ('turkmen', 'Turkman'), ('other', 'Boshqa')], default='uzbek', max_length=20, verbose_name='Millati'),
        ),
    ]
