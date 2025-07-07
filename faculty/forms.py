from django import forms
from django.contrib.auth import get_user_model
from .models import Faculty, Group

User = get_user_model()


class FacultyForm(forms.ModelForm):
    dean = forms.ModelChoiceField(
        queryset=User.objects.filter(user_type='dean'),
        required=False,
        empty_label="Dekan tanlang",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Faculty
        fields = ['name', 'description', 'dean']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fakultet nomi'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Fakultet haqida qisqacha ma\'lumot'}),
        }


class GroupForm(forms.ModelForm):
    tutor = forms.ModelChoiceField(
        queryset=User.objects.filter(user_type='tutor'),
        required=False,
        empty_label="Tutor tanlang",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Group
        fields = ['name', 'course', 'tutor', 'faculty']  # faculty qo'shildi
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Guruh nomi'}),
            'course': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 6}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),  # faculty uchun widget
        }

    def __init__(self, *args, **kwargs):
        faculty = kwargs.pop('faculty', None)
        super().__init__(*args, **kwargs)
        if faculty:
            # Agar faculty berilgan bo'lsa, tutorlarni shu faculty bo'yicha filtrlang
            self.fields['tutor'].queryset = User.objects.filter(user_type='tutor', faculty=faculty)
            # Faculty maydonini faqat bitta qiymat bilan cheklash (ixtiyoriy)
            self.fields['faculty'].queryset = Faculty.objects.filter(id=faculty.id)
            self.fields['faculty'].initial = faculty  # Default qiymat sifatida faculty