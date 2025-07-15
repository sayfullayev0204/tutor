from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Student, TTJ
from housing.models import HousingInspection
from .forms import StudentForm
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from .models import District
from datetime import datetime
import openpyxl
from openpyxl.utils import get_column_letter

@login_required
def student_list(request):
    user = request.user
    
    # Determine queryset based on user role
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
    
    # Filter by gender
    gender = request.GET.get('gender')
    if gender:
        students = students.filter(gender=gender)
    
    # Filter by apartment type
    appartment_type = request.GET.get('appartment_type')
    if appartment_type:
        students = students.filter(appartment_type=appartment_type)
    
    # Filter by bully_student
    bully_student = request.GET.get('bully_student')
    if bully_student in ['true', 'false']:
        bully_student_bool = bully_student == 'true'
        students = students.filter(bully_student=bully_student_bool)
    
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

def get_districts(request):
    region_id = request.GET.get('region')
    districts = District.objects.filter(region_id=region_id).values('id', 'name')
    return JsonResponse(list(districts), safe=False)



@login_required
def export_students_to_excel(request):
    user = request.user
    
    # Determine queryset based on user role
    if user.is_rector():
        students = Student.objects.all()
    elif user.is_dean():
        students = Student.objects.filter(group__faculty=user.faculty) if user.faculty else Student.objects.none()
    elif user.is_tutor():
        students = Student.objects.filter(group__tutor=user)
    else:
        students = Student.objects.none()
    
    # Apply the same filters as in student_list
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
    
    gender = request.GET.get('gender')
    if gender:
        students = students.filter(gender=gender)
    
    appartment_type = request.GET.get('appartment_type')
    if appartment_type:
        students = students.filter(appartment_type=appartment_type)
    
    bully_student = request.GET.get('bully_student')
    if bully_student in ['true', 'false']:
        bully_student_bool = bully_student == 'true'
        students = students.filter(bully_student=bully_student_bool)
    
    # Create Excel workbook and sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Talabalar"
    
    # Define headers
    headers = [
        "ID", "F.I.O", "Jinsi", "Tug'ilgan sana", "Yoshi", "Guruh", "Fakultet", "Talaba ID", 
        "JSHSHIR", "Pasport", "OTM", "Ta'lim turi", "To'lov turi", "Ta'lim shakli", 
        "Shifr", "Mutaxassislik", "Fuqarolik", "Vatan", "Doimiy viloyat", "Doimiy tuman", 
        "Vaqtincha viloyat", "Vaqtincha tuman", "Yashash manzili", "Yashash turi", 
        "Oilaviy holati", "Telefon raqami", "Email", "Yetim", "Nogironligi bor", 
        "Bezori talaba", "TTJ", "Ijara xona", "Yaratilgan sana"
    ]
    ws.append(headers)
    
    # Write student data
    for student in students:
        row = [
            student.id,
            student.full_name,
            dict(Student.GENDER_CHOICES).get(student.gender, '-'),
            student.birth_date.strftime('%d.%m.%Y') if student.birth_date else '-',
            student.age if student.birth_date else '-',
            student.group.name if student.group else '-',
            student.group.faculty.name if student.group and student.group.faculty else '-',
            student.student_id,
            student.jshshir,
            student.passport,
            student.otm,
            dict(Student.TALIM_CHOICES).get(student.talim_turi, '-'),
            dict(Student.TULOV_CHOICES).get(student.tulov_turi, '-'),
            dict(Student.TALIM_SHAKLI_CHOICES).get(student.talim_shakli, '-'),
            student.shifr,
            student.mutaxassislik.name if student.mutaxassislik else '-',
            dict(Student.FUQARO_CHOICES).get(student.fuqaro, '-'),
            student.country.name if student.country else '-',
            student.const_region.name if student.const_region else '-',
            student.const_district.name if student.const_district else '-',
            student.temporary_region.name if student.temporary_region else '-',
            student.temporary_district.name if student.temporary_district else '-',
            student.temporary_address or '-',
            dict(Student.APPARTMENT_TYPE_CHOICES).get(student.appartment_type, '-'),
            dict(Student.FAMILY_CHOICES).get(student.family_type, '-'),
            student.phone_number or '-',
            student.email or '-',
            'Ha' if student.is_orphan else 'Yo‘q',
            'Ha' if student.has_disability else 'Yo‘q',
            'Ha' if student.bully_student else 'Yo‘q',
            student.ttj.name if student.ttj else '-',
            student.room.address if student.room else '-',
            student.created_at.strftime('%d.%m.%Y %H:%M') if student.created_at else '-'
        ]
        ws.append(row)
    
    # Adjust column widths
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 15
    
    # Create HTTP response with Excel file
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="Talabalar_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    
    # Save workbook to response
    wb.save(response)
    return response

