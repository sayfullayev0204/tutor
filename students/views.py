from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Student, TTJ
from housing.models import HousingInspection
from .forms import StudentForm
from django.core.exceptions import PermissionDenied

@login_required
def student_list(request):
    user = request.user
    
    if hasattr(user, 'is_rector') and user.is_rector():
        students = Student.objects.all()
    elif hasattr(user, 'is_dean') and user.is_dean():
        students = Student.objects.filter(group__faculty=user.faculty) if user.faculty else Student.objects.none()
    elif hasattr(user, 'is_tutor') and user.is_tutor():
        students = Student.objects.filter(group__tutor=user)
    else:
        students = Student.objects.none()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(middle_name__icontains=search_query) |
            Q(group__name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(jshshir__icontains=search_query) |
            Q(passport__icontains=search_query)
        )
    
    context = {
        'students': students,
        'search_query': search_query,
    }
    return render(request, 'students/student_list.html', context)

@login_required
def student_detail(request, pk):
    user = request.user
    
    if hasattr(user, 'is_rector') and user.is_rector():
        student = get_object_or_404(Student, pk=pk)
    elif hasattr(user, 'is_dean') and user.is_dean():
        student = get_object_or_404(Student, pk=pk, group__faculty=user.faculty)
    elif hasattr(user, 'is_tutor') and user.is_tutor():
        student = get_object_or_404(Student, pk=pk, group__tutor=user)
    else:
        messages.error(request, "Sizga bu talabani ko'rish uchun ruxsat yo'q.")
        return redirect('dashboard')
    
    inspections = HousingInspection.objects.filter(student=student).order_by('-inspection_date')
    
    context = {
        'student': student,
        'inspections': inspections,
    }
    return render(request, 'students/student_detail.html', context)

@login_required
def renting_students(request):
    user = request.user
    
    if hasattr(user, 'is_rector') and user.is_rector():
        students = Student.objects.filter(appartment_type='rent')
    elif hasattr(user, 'is_dean') and user.is_dean():
        students = Student.objects.filter(appartment_type='rent', group__faculty=user.faculty) if user.faculty else Student.objects.none()
    elif hasattr(user, 'is_tutor') and user.is_tutor():
        students = Student.objects.filter(appartment_type='rent', group__tutor=user)
    else:
        students = Student.objects.none()
    
    context = {
        'students': students,
    }
    return render(request, 'students/renting_students.html', context)

@login_required
def dormitory_students(request):
    user = request.user
    
    if hasattr(user, 'is_rector') and user.is_rector():
        students = Student.objects.filter(appartment_type='ttj')
    elif hasattr(user, 'is_dean') and user.is_dean():
        students = Student.objects.filter(appartment_type='ttj', group__faculty=user.faculty) if user.faculty else Student.objects.none()
    elif hasattr(user, 'is_tutor') and user.is_tutor():
        students = Student.objects.filter(appartment_type='ttj', group__tutor=user)
    else:
        students = Student.objects.none()
    
    context = {
        'students': students,
    }
    return render(request, 'students/dormitory_students.html', context)

@login_required
def orphan_students(request):
    user = request.user
    
    if hasattr(user, 'is_rector') and user.is_rector():
        students = Student.objects.filter(is_orphan=True)
    elif hasattr(user, 'is_dean') and user.is_dean():
        students = Student.objects.filter(is_orphan=True, group__faculty=user.faculty) if user.faculty else Student.objects.none()
    elif hasattr(user, 'is_tutor') and user.is_tutor():
        students = Student.objects.filter(is_orphan=True, group__tutor=user)
    else:
        students = Student.objects.none()
    
    context = {
        'students': students,
    }
    return render(request, 'students/orphan_students.html', context)

@login_required
def disabled_students(request):
    user = request.user
    
    if hasattr(user, 'is_rector') and user.is_rector():
        students = Student.objects.filter(has_disability=True)
    elif hasattr(user, 'is_dean') and user.is_dean():
        students = Student.objects.filter(has_disability=True, group__faculty=user.faculty) if user.faculty else Student.objects.none()
    elif hasattr(user, 'is_tutor') and user.is_tutor():
        students = Student.objects.filter(has_disability=True, group__tutor=user)
    else:
        students = Student.objects.none()
    
    context = {
        'students': students,
    }
    return render(request, 'students/disabled_students.html', context)

@login_required
def student_create(request):
    if not (hasattr(request.user, 'is_tutor') and request.user.is_tutor()):
        messages.error(request, "Faqat guruh tutorlari talaba qo'sha oladi.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if 'room' in request.POST and request.POST['room'] == StudentForm.ADD_NEW_ROOM:
            request.session['student_form_data'] = request.POST.dict()
            request.session['return_to'] = 'student_create'
            return redirect('room_create')
        
        if form.is_valid():
            student = form.save(commit=False)
            if student.group.tutor != request.user:
                messages.error(request, "Siz faqat o'zingiz boshqaradigan guruhga talaba qo'sha olasiz.")
                return render(request, 'students/student_form.html', {'form': form, 'title': 'Yangi talaba qo‘shish'})
            try:
                student.save()
                messages.success(request, f"{student.full_name} muvaffaqiyatli qo'shildi.")
                request.session.pop('student_form_data', None)
                request.session.pop('return_to', None)
                return redirect('student_list')
            except Exception as e:
                messages.error(request, f"Ma'lumotni saqlashda xato: {str(e)}")
        else:
            messages.error(request, f"Forma xatolarni tuzating: {form.errors.as_text()}")
    else:
        initial_data = request.session.get('student_form_data', {})
        form = StudentForm(initial=initial_data)
        form.fields['group'].queryset = form.fields['group'].queryset.filter(tutor=request.user)
    
    context = {
        'form': form,
        'title': 'Yangi talaba qo‘shish',
    }
    return render(request, 'students/student_form.html', context)

@login_required
def student_edit(request, pk):
    if not (hasattr(request.user, 'is_tutor') and request.user.is_tutor()):
        messages.error(request, "Faqat guruh tutorlari talaba ma'lumotlarini tahrirlashi mumkin.")
        return redirect('dashboard')
    
    student = get_object_or_404(Student, pk=pk, group__tutor=request.user)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        # Check if the form submission is explicitly for adding a new room
        if 'room' in request.POST and request.POST['room'] == StudentForm.ADD_NEW_ROOM and request.POST.get('add_new_room') == 'true':
            request.session['student_form_data'] = request.POST.dict()
            request.session['return_to'] = 'student_edit'
            request.session['student_pk'] = pk
            return redirect('room_create')
        
        if form.is_valid():
            student = form.save(commit=False)
            if student.group.tutor != request.user:
                messages.error(request, "Siz faqat o'zingiz boshqaradigan guruhdagi talabani tahrirlashingiz mumkin.")
                return render(request, 'students/student_form.html', {'form': form, 'student': student, 'title': 'Talaba ma‘lumotlarini tahrirlash'})
            try:
                student.save()
                messages.success(request, f"{student.full_name} ma'lumotlari muvaffaqiyatli yangilandi.")
                request.session.pop('student_form_data', None)
                request.session.pop('return_to', None)
                request.session.pop('student_pk', None)
                # Re-render the edit page instead of redirecting
                form = StudentForm(instance=student)
                form.fields['group'].queryset = form.fields['group'].queryset.filter(tutor=request.user)
                return render(request, 'students/student_form.html', {
                    'form': form,
                    'student': student,
                    'title': 'Talaba ma‘lumotlarini tahrirlash',
                })
            except Exception as e:
                messages.error(request, f"Ma'lumotni saqlashda xato: {str(e)}")
        else:
            messages.error(request, f"Forma xatolarni tuzating: {form.errors.as_text()}")
    else:
        initial_data = request.session.get('student_form_data', {})
        form = StudentForm(instance=student, initial=initial_data)
        form.fields['group'].queryset = form.fields['group'].queryset.filter(tutor=request.user)
    
    context = {
        'form': form,
        'student': student,
        'title': 'Talaba ma‘lumotlarini tahrirlash',
    }
    return render(request, 'students/student_form.html', context)

@login_required
def student_delete(request, pk):
    if not (hasattr(request.user, 'is_tutor') and request.user.is_tutor()):
        messages.error(request, "Faqat guruh tutorlari talabani o'chirishi mumkin.")
        return redirect('dashboard')
    
    student = get_object_or_404(Student, pk=pk, group__tutor=request.user)
    
    if request.method == 'POST':
        student_name = student.full_name
        student.delete()
        messages.success(request, f"{student_name} muvaffaqiyatli o'chirildi.")
        return redirect('student_list')
    
    context = {
        'student': student,
        'title': 'Talabani o‘chirish',
    }
    return render(request, 'students/student_confirm_delete.html', context)

from django.http import JsonResponse
from .models import District

def get_districts(request):
    region_id = request.GET.get('region')
    districts = District.objects.filter(region_id=region_id).values('id', 'name')
    return JsonResponse(list(districts), safe=False)

