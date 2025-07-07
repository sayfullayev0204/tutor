from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from faculty.models import Faculty, Group
from students.models import Student
from housing.models import HousingInspection
from accounts.decorators import rector_required, dean_required, tutor_required
from django.db import models

@login_required
def dashboard(request):
    user = request.user
    if user.is_rector():
        return redirect('rector_dashboard')
    elif user.is_dean():
        return redirect('dean_dashboard')
    elif user.is_tutor():
        return redirect('tutor_dashboard')
    return redirect('login')


@rector_required
def rector_dashboard(request):
    faculties = Faculty.objects.all().annotate(
        groups_count=Count('groups'),
        students_count=Count('groups__students')
    )
    inspections = HousingInspection.objects.all()
    
    context = {
        'faculties': faculties,
        'total_students': Student.objects.count(),
        'renting_students': Student.objects.filter(is_renting=True).count(),
        'dormitory_students': Student.objects.filter(lives_in_dormitory=True).count(),
        'orphan_students': Student.objects.filter(is_orphan=True).count(),
        'disabled_students': Student.objects.filter(has_disability=True).count(),
        'inspections': inspections,
        'pending_inspections': inspections.filter(status='pending').count(),
        'approved_inspections': inspections.filter(status='approved').count(),
        'rejected_inspections': inspections.filter(status='rejected').count(),
    }
    return render(request, 'dashboard/rector_dashboard.html', context)


@dean_required
def dean_dashboard(request):
    user = request.user
    faculty = user.faculty
    
    if not faculty:
        return redirect('dashboard')
    
    groups = Group.objects.filter(faculty=faculty)
    students = Student.objects.filter(group__faculty=faculty)
    inspections = HousingInspection.objects.filter(student__group__faculty=faculty)
    
    context = {
        'faculty': faculty,
        'groups': groups,
        'total_students': students.count(),
        'renting_students': students.filter(is_renting=True).count(),
        'dormitory_students': students.filter(lives_in_dormitory=True).count(),
        'orphan_students': students.filter(is_orphan=True).count(),
        'disabled_students': students.filter(has_disability=True).count(),
        'inspections': inspections,
        'pending_inspections': inspections.filter(status='pending'),
        'approved_inspections': inspections.filter(status='approved').count(),
        'rejected_inspections': inspections.filter(status='rejected').count(),
    }
    return render(request, 'dashboard/dean_dashboard.html', context)


@tutor_required
def tutor_dashboard(request):
    user = request.user
    groups = Group.objects.filter(tutor=user)
    students = Student.objects.filter(group__in=groups)
    
    context = {
        'groups': groups,
        'total_students': students.count(),
        'renting_students': students.filter(is_renting=True),
        'dormitory_students': students.filter(lives_in_dormitory=True).count(),
        'orphan_students': students.filter(is_orphan=True).count(),
        'disabled_students': students.filter(has_disability=True).count(),
        'male_students': students.filter(gender='male').count(),
        'female_students': students.filter(gender='female').count(),
        'recent_inspections': HousingInspection.objects.filter(inspector=user).order_by('-inspection_date')[:5],
    }
    return render(request, 'dashboard/tutor_dashboard.html', context)


@rector_required
def statistics(request):
    # Overall statistics
    total_students = Student.objects.count()
    total_faculties = Faculty.objects.count()
    total_groups = Group.objects.count()
    total_inspections = HousingInspection.objects.count()
    
    # Student statistics by category
    renting_students = Student.objects.filter(is_renting=True).count()
    dormitory_students = Student.objects.filter(lives_in_dormitory=True).count()
    orphan_students = Student.objects.filter(is_orphan=True).count()
    disabled_students = Student.objects.filter(has_disability=True).count()
    
    # Gender statistics
    male_students = Student.objects.filter(gender='male').count()
    female_students = Student.objects.filter(gender='female').count()
    
    # Inspection statistics
    pending_inspections = HousingInspection.objects.filter(status='pending').count()
    approved_inspections = HousingInspection.objects.filter(status='approved').count()
    rejected_inspections = HousingInspection.objects.filter(status='rejected').count()
    
    # Faculty-wise statistics
    faculty_stats = Faculty.objects.annotate(
        students_count=Count('groups__students'),
        groups_count=Count('groups'),
        renting_count=Count('groups__students', filter=models.Q(groups__students__is_renting=True)),
        inspections_count=Count('groups__students__housing_inspections')
    )
    
    context = {
        'total_students': total_students,
        'total_faculties': total_faculties,
        'total_groups': total_groups,
        'total_inspections': total_inspections,
        'renting_students': renting_students,
        'dormitory_students': dormitory_students,
        'orphan_students': orphan_students,
        'disabled_students': disabled_students,
        'male_students': male_students,
        'female_students': female_students,
        'pending_inspections': pending_inspections,
        'approved_inspections': approved_inspections,
        'rejected_inspections': rejected_inspections,
        'faculty_stats': faculty_stats,
    }
    return render(request, 'dashboard/statistics.html', context)
