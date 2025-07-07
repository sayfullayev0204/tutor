from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Faculty, Group
from .forms import FacultyForm, GroupForm
from accounts.decorators import rector_required, dean_required, tutor_required
from students.models import Student
from django.contrib.auth.models import User


@login_required
def faculty_list(request):
    user = request.user
    
    if user.is_rector():
        faculties = Faculty.objects.annotate(
            groups_count=Count('groups'),
            students_count=Count('groups__students')
        ).order_by('name')
    elif user.is_dean():
        faculties = Faculty.objects.filter(id=user.faculty.id) if user.faculty else Faculty.objects.none()
    else:
        faculties = Faculty.objects.none()
    
    context = {
        'faculties': faculties,
    }
    return render(request, 'faculty/faculty_list.html', context)


@login_required
def faculty_detail(request, pk):
    user = request.user
    
    if user.is_rector():
        faculty = get_object_or_404(Faculty, pk=pk)
    elif user.is_dean():
        faculty = get_object_or_404(Faculty, pk=pk, id=user.faculty.id)
    else:
        faculty = get_object_or_404(Faculty, pk=pk)
    
    groups = faculty.groups.all()
    
    context = {
        'faculty': faculty,
        'groups': groups,
    }
    return render(request, 'faculty/faculty_detail.html', context)


@rector_required
def faculty_create(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            faculty = form.save()
            messages.success(request, f'Fakultet "{faculty.name}" muvaffaqiyatli yaratildi.')
            return redirect('faculty_list')
    else:
        form = FacultyForm()
    
    context = {
        'form': form,
        'title': 'Yangi fakultet yaratish',
    }
    return render(request, 'faculty/faculty_form.html', context)


@rector_required
def faculty_edit(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    
    if request.method == 'POST':
        form = FacultyForm(request.POST, instance=faculty)
        if form.is_valid():
            faculty = form.save()
            messages.success(request, f'Fakultet "{faculty.name}" muvaffaqiyatli yangilandi.')
            return redirect('faculty_list')
    else:
        form = FacultyForm(instance=faculty)
    
    context = {
        'form': form,
        'faculty': faculty,
        'title': f'"{faculty.name}" fakultetini tahrirlash',
    }
    return render(request, 'faculty/faculty_form.html', context)


@rector_required
def faculty_delete(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    
    if request.method == 'POST':
        faculty_name = faculty.name
        faculty.delete()
        messages.success(request, f'Fakultet "{faculty_name}" muvaffaqiyatli o\'chirildi.')
        return redirect('faculty_list')
    
    context = {
        'faculty': faculty,
    }
    return render(request, 'faculty/faculty_confirm_delete.html', context)


@login_required
def group_list(request):
    user = request.user
    
    if user.is_rector():
        groups = Group.objects.all()
    elif user.is_dean():
        if not user.faculty:
            print(f"Xatolik: {user} uchun faculty topilmadi")
            groups = Group.objects.none()
        else:
            groups = Group.objects.filter(faculty=user.faculty)
            print(f"Faculty: {user.faculty}, Guruhlar soni: {groups.count()}")
    elif user.is_tutor():
        groups = Group.objects.filter(tutor=user)
    else:
        groups = Group.objects.none()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        groups = groups.filter(
            Q(name__icontains=search_query) |
            Q(faculty__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(groups, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'faculty/group_list.html', context)

@login_required
def group_detail(request, pk):
    user = request.user
    
    if user.is_rector():
        group = get_object_or_404(Group, pk=pk)
    elif user.is_dean():
        group = get_object_or_404(Group, pk=pk, faculty=user.faculty)
    elif user.is_tutor():
        group = get_object_or_404(Group, pk=pk, tutor=user)
    else:
        return redirect('dashboard')
    
    students = group.students.all().order_by('last_name', 'first_name')
    
    context = {
        'group': group,
        'students': students,
    }
    return render(request, 'faculty/group_detail.html', context)


@dean_required
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST, faculty=request.user.faculty)
        if form.is_valid():
            group = form.save(commit=False)
            group.faculty = request.user.faculty
            group.save()
            messages.success(request, f'Guruh "{group.name}" muvaffaqiyatli yaratildi.')
            return redirect('group_list')
    else:
        form = GroupForm(faculty=request.user.faculty)
    
    context = {
        'form': form,
        'title': 'Yangi guruh yaratish',
    }
    return render(request, 'faculty/group_form.html', context)


@dean_required
def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk, faculty=request.user.faculty)
    
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group, faculty=request.user.faculty)
        if form.is_valid():
            group = form.save()
            messages.success(request, f'Guruh "{group.name}" muvaffaqiyatli yangilandi.')
            return redirect('group_list')
    else:
        form = GroupForm(instance=group, faculty=request.user.faculty)
    
    context = {
        'form': form,
        'group': group,
        'title': f'"{group.name}" guruhini tahrirlash',
    }
    return render(request, 'faculty/group_form.html', context)


@dean_required
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk, faculty=request.user.faculty)
    
    if request.method == 'POST':
        group_name = group.name
        group.delete()
        messages.success(request, f'Guruh "{group_name}" muvaffaqiyatli o\'chirildi.')
        return redirect('group_list')
    
    context = {
        'group': group,
    }
    return render(request, 'faculty/group_confirm_delete.html', context)
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from .models import Faculty, Group
from django import forms

User = get_user_model()

# Tutor Form
class TutorForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'faculty', 'phone_number', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Foydalanuvchi nomi'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ism'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Familiya'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefon raqami'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        faculty = kwargs.pop('faculty', None)
        super().__init__(*args, **kwargs)
        if faculty:
            self.fields['faculty'].queryset = Faculty.objects.filter(id=faculty.id)
            self.fields['faculty'].initial = faculty
        # Allow clearing the profile picture
        self.fields['profile_picture'].required = False
# Tutor List View
@login_required
def tutor_list(request):
    user = request.user
    
    if user.is_rector():
        tutors = User.objects.filter(user_type='tutor')
        print(f"Rektor: {tutors.count()} tutors found")
    elif user.is_dean():
        if not user.faculty:
            print(f"Xatolik: {user} uchun fakultet topilmadi")
            tutors = User.objects.none()
        else:
            tutors = User.objects.filter(
                user_type='tutor',
                assigned_groups__faculty=user.faculty
            ).distinct()
            print(f"Dekan: {tutors.count()} tutors found for faculty {user.faculty}")
    else:
        print(f"Foydalanuvchi {user} dashboard'ga yo'naltirilmoqda")
        return redirect('dashboard')
    
    # Annotate with group and student counts
    tutors = tutors.annotate(
        groups_count=Count('assigned_groups'),
        students_count=Count('assigned_groups__students')
    )
    
    context = {
        'tutors': tutors,
        'title': 'Tutorlar ro\'yxati',
    }
    return render(request, 'faculty/tutor_list.html', context)

# Tutor Detail View (from previous response)
@login_required
def tutor_detail(request, tutor_id):
    user = request.user
    tutor = get_object_or_404(User, id=tutor_id, user_type='tutor')
    
    # Restrict access to rector or dean of the tutor's faculty
    if not (user.is_rector() or (user.is_dean() and user.faculty == tutor.faculty)):
        messages.error(request, "Sizda ushbu tutorga kirish huquqi yo‘q.")
        return redirect('dashboard')
    
    # Get groups assigned to the tutor
    groups = Group.objects.filter(tutor=tutor)

    
    context = {
        'tutor': tutor,
        'groups': groups,
        'title': f"{tutor.get_full_name()} - Tutor ma'lumotlari",
    }
    return render(request, 'faculty/tutor_detail.html', context)
# Tutor Create View
@login_required
def tutor_create(request):
    user = request.user
    
    if not (user.is_rector() or user.is_dean()):
        messages.error(request, "Sizda yangi tutor yaratish huquqi yo‘q.")
        return redirect('dashboard')
    
    faculty = user.faculty if user.is_dean() else None
    
    if request.method == 'POST':
        form = TutorForm(request.POST, request.FILES, faculty=faculty)
        if form.is_valid():
            tutor = form.save(commit=False)
            tutor.user_type = 'tutor'
            tutor.set_password('default_password')  # Change this for production
            if user.is_dean():
                tutor.faculty = user.faculty
            tutor.save()
            messages.success(request, f"Tutor {tutor.get_full_name()} muvaffaqiyatli yaratildi.")
            return redirect('tutor_list')
    else:
        form = TutorForm(faculty=faculty)
    
    context = {
        'form': form,
        'title': 'Yangi tutor yaratish',
    }
    return render(request, 'faculty/tutor_form.html', context)

# Tutor Edit View
@login_required
def tutor_edit(request, tutor_id):
    user = request.user
    tutor = get_object_or_404(User, id=tutor_id, user_type='tutor')
    
    if not (user.is_rector() or (user.is_dean() and user.faculty == tutor.faculty)):
        messages.error(request, "Sizda ushbu tutorni tahrirlash huquqi yo‘q.")
        return redirect('dashboard')
    
    faculty = user.faculty if user.is_dean() else None
    
    if request.method == 'POST':
        form = TutorForm(request.POST, request.FILES or None, instance=tutor, faculty=faculty)
        if form.is_valid():
            tutor = form.save(commit=False)
            # Handle profile picture clearing
            if 'profile_picture-clear' in request.POST and request.POST['profile_picture-clear'] == 'on':
                tutor.profile_picture.delete(save=False)  # Delete the existing file
                tutor.profile_picture = None
            tutor.save()
            messages.success(request, f"Tutor {tutor.get_full_name()} ma'lumotlari yangilandi.")
            return redirect('tutor_list')
        else:
            messages.error(request, "Xatolik yuz berdi. Iltimos, shaklni tekshiring.")
    else:
        form = TutorForm(instance=tutor, faculty=faculty)
    
    context = {
        'form': form,
        'tutor': tutor,
        'title': f"{tutor.get_full_name()} - Ma'lumotlarni tahrirlash",
    }
    return render(request, 'faculty/tutor_form.html', context)

