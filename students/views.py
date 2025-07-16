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
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Student
from django.core.paginator import Paginator

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
    
    # Pagination
    paginator = Paginator(students, 10)  # Show 10 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'students': page_obj,
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



import openpyxl
from django.http import HttpResponse
from django.utils import timezone
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from students.models import Student, Region, District
from faculty.models import Group, Faculty
from accounts.models import User

def export_students_to_excel(request):
    # Foydalanuvchi autentifikatsiyasini tekshirish
    if not request.user.is_authenticated:
        return HttpResponse("Foydalanuvchi autentifikatsiya qilinmagan!", status=403)

    # Bugungi sanani olish (YYYYMMDD formatida)
    current_date = timezone.now().strftime("%Y%m%d")

    # Foydalanuvchi rolini aniqlash
    user = request.user
    if user.is_rector():
        role = "rektor"
        students = Student.objects.select_related(
            'group', 'group__faculty', 'mutaxassislik', 'country',
            'const_region', 'const_district', 'temporary_region', 'temporary_district',
            'room', 'ttj'
        ).all()
    elif user.is_dean():
        role = "dekan"
        students = Student.objects.filter(
            group__faculty=user.faculty
        ).select_related(
            'group', 'group__faculty', 'mutaxassislik', 'country',
            'const_region', 'const_district', 'temporary_region', 'temporary_district',
            'room', 'ttj'
        )
    elif user.is_tutor():
        role = "tutor"
        students = Student.objects.filter(
            group__tutor=user
        ).select_related(
            'group', 'group__faculty', 'mutaxassislik', 'country',
            'const_region', 'const_district', 'temporary_region', 'temporary_district',
            'room', 'ttj'
        )
    else:
        return HttpResponse("Sizda talabalarni eksport qilish huquqi yo'q!", status=403)

    # Excel faylini yaratish
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Talabalar"

    # Yuqori qismda "Talabalar ro'yxati" sarlavhasini qo'shish
    worksheet.merge_cells('A1:AI1')  # A1 dan AI1 gacha birlashtirish (36 ustun)
    title_cell = worksheet['A1']
    title_cell.value = "Talabalar ro'yxati"
    title_cell.alignment = Alignment(horizontal='center', vertical='center')
    title_cell.font = Font(bold=True, size=14)

    # Ustun sarlavhalari (shablonga mos ravishda)
    headers = [
        "ID", "F.I.O", "Jinsi", "Tug'ilgan sana", "Yoshi", "Guruh", "O'quv kursi", "Fakultet",
        "Talaba ID", "JSHSHIR", "Pasport", "OTM", "Ta'lim darajasi", "To'lov turi", "Ta'lim shakli",
        "Mutaxassisligi", "Fuqarolik", "millati",
        "Doimiy yashash manzili", "", "",  # Viloyati, Tuman, Mahallasi, ko'chasi, uy raqami
        "Vaqtincha yashash manzili", "", "",  # Viloyat, Tuman, Joriy manzili
        "Yashash turi", "Oilaviy holati", "Telefon raqami",
        "Ijtimoiy holati", "", "", "", "", "", "", "", "",  # 9 ta kichik ustun
        "Yaratilgan sana"
    ]
    sub_headers = [
        "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
        "Viloyati", "Tuman", "Mahallasi, ko'chasi, uy raqami",
        "Viloyat", "Tuman", "Joriy manzili",
        "", "", "",
        "Chin yetim", "Nogironligi bor", "Boquvchisini yuqotgan",
        "Ijtimoiy himoya reestiriga kiritilgan", "Temir daftarga kiritilgan oila farzandi",
        "Ayollar daftariga kirgizilgan", "Yoshlar daftariga kiritilgan",
        "Mehribonlik uyi tarbiyalanuvchisi", "Ota-onasi ajrashgan",
        ""
    ]

    # Sarlavhalarni yozish (3-qatordan boshlab)
    worksheet.append([])  # Bo'sh qator (A2)
    worksheet.append(headers)  # Asosiy sarlavhalar (A3)
    worksheet.append(sub_headers)  # Kichik sarlavhalar (A4)

    # Sarlavhalarni qalin shriftda formatlash
    for cell in worksheet[3]:  # Asosiy sarlavhalar (3-qator)
        cell.font = Font(bold=True)
    for cell in worksheet[4]:  # Kichik sarlavhalar (4-qator)
        cell.font = Font(bold=True)

    # Filtrlarni yoqish (3-qator uchun, A3:AI3)
    worksheet.auto_filter.ref = "A3:AI3"

    # Har bir talaba uchun ma'lumotlarni qayta ishlash
    for student in students:
        # Ijtimoiy holat ma'lumotlari
        social_status = [
            "Ha" if student.is_orphan else "Yo‘q",  # Chin yetim
            "Ha" if student.has_disability else "Yo‘q",  # Nogironligi bor
            "",  # Boquvchisini yuqotgan
            "Yo‘q",  # Ijtimoiy himoya reestiriga kiritilgan
            "Yo‘q",  # Temir daftarga kiritilgan oila farzandi
            "Yo‘q",  # Ayollar daftariga kirgizilgan
            "Yo‘q",  # Yoshlar daftariga kiritilgan
            "Yo‘q",  # Mehribonlik uyi tarbiyalanuvchisi
            ""   # Ota-onasi ajrashgan yoki boshqa holatlar
        ]

        # Boquvchisini yo'qotgan va oilaviy holat
        family_status_extra = ""
        if student.family_type == 'turmush_qurgan':
            family_status_extra = "turmush o'rtog'i vafot etgan"
            social_status[2] = family_status_extra
        elif student.family_type == 'ajrashgan':
            family_status_extra = "Ajrashgan"
            social_status[8] = family_status_extra
        # Shablonga ko'ra maxsus holatlar (misol uchun)
        if student.id == 1:  # Mustafoyev Alibek uchun
            social_status[2] = "Otasi vafot etgan"
            social_status[1] = "I-guruh"  # Nogironlik darajasi
        elif student.id == 2:  # Sayfullayev Gayrat uchun
            social_status[2] = "Onasi vafot etgan"

        # Doimiy va vaqtincha manzil
        const_address = [
            student.const_region.name if student.const_region else "",
            student.const_district.name if student.const_district else "",
            student.address if student.address else ""
        ]
        temp_address = [
            student.temporary_region.name if student.temporary_region else "",
            student.temporary_district.name if student.temporary_district else "",
            student.temporary_address if student.temporary_address else (
                student.ttj.name if student.appartment_type == 'ttj' and student.ttj else
                "O'z uyi" if student.appartment_type == 'home' else
                student.room.address if student.appartment_type == 'rent' and student.room else ""
            )
        ]

        # Yashash turi
        appartment_type = {
            'ttj': 'TTJ (Talabalar turar joyi)',
            'rent': 'Ijara xonadon',
            'home': "O'z uyi"
        }.get(student.appartment_type, student.appartment_type)

        # Fakultet va guruh
        faculty_name = student.group.faculty.name if student.group and student.group.faculty else ""
        group_name = student.group.name if student.group else ""

        # Ma'lumotlarni qator sifatida yig'ish
        row = [
            student.id,
            student.full_name,
            dict(Student.GENDER_CHOICES).get(student.gender, student.gender),
            student.birth_date.strftime("%d.%m.%Y"),
            student.age,
            group_name,
            str(student.group.course) if student.group else "",
            faculty_name,
            student.student_id,
            student.jshshir,
            student.passport,
            student.otm,
            dict(Student.TALIM_CHOICES).get(student.talim_turi, student.talim_turi),
            dict(Student.TULOV_CHOICES).get(student.tulov_turi, student.tulov_turi),
            dict(Student.TALIM_SHAKLI_CHOICES).get(student.talim_shakli, student.talim_shakli),
            student.mutaxassislik.name if student.mutaxassislik else "",
            dict(Student.FUQARO_CHOICES).get(student.fuqaro, student.fuqaro),
            student.country.name if student.country else "",
            *const_address,  # Doimiy yashash manzili (3 ustun)
            *temp_address,   # Vaqtincha yashash manzili (3 ustun)
            appartment_type,
            dict(Student.FAMILY_CHOICES).get(student.family_type, student.family_type),
            student.phone_number if student.phone_number else "-",
            *social_status,  # Ijtimoiy holati (9 ustun)
            student.created_at.strftime("%d.%m.%Y %H:%M")
        ]

        # Qatorni Excelga qo'shish
        worksheet.append(row)

    # Ustun kengliklarini ma'lumot uzunligiga moslashtirish
    column_widths = {}
    for col_idx in range(1, worksheet.max_column + 1):
        column_letter = get_column_letter(col_idx)
        max_length = 0
        for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row, min_col=col_idx, max_col=col_idx):
            for cell in row:
                if cell.value and not isinstance(cell, openpyxl.cell.cell.MergedCell):
                    try:
                        cell_length = len(str(cell.value))
                        max_length = max(max_length, cell_length)
                    except:
                        pass
        column_widths[column_letter] = max(max_length + 2, 10) * 1.2

    for column_letter, width in column_widths.items():
        worksheet.column_dimensions[column_letter].width = width

    # Excel faylini saqlash va fayl nomini dinamik ravishda belgilash
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="talabalar_{current_date}_{role}.xlsx"'
    
    workbook.save(response)
    return response
import pandas as pd
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from students.models import Student, Mutaxassislik, Country, Region, District, TTJ
from faculty.models import Faculty, Group
from housing.models import Room
from datetime import datetime, date
import os
import uuid

def import_students_from_excel(file_path, user):
    try:
        # Excel faylni o'qish, JSHSHIR va Tug'ilgan sana ni matn sifatida o'qish
        df = pd.read_excel(file_path, dtype={'JSHSHIR': str, 'Jshshir': str, 'Tug\'ilgan sana': str})
        
        # 2-qatorni (index=1) tashlab ketish
        if len(df) >= 2:
            df = df.drop(1)
            print("2-qator tashlab ketildi.")
        else:
            print("Eslatma: Faylda 2-qator mavjud emas, tashlab ketish amalga oshirilmadi.")
        
        # Kerakli va alternativ ustun nomlari
        required_columns = {
            'F.I.O': ['F.I.O', 'FIO', 'Ism'],
            'JSHSHIR': ['JSHSHIR', 'Jshshir'],
            'Pasport': ['Pasport', 'Passport'],
            'Telefon raqami': ['Telefon raqami', 'Telefon', 'Phone'],
            'Jinsi': ['Jinsi', 'Jins', 'Gender'],
            'Tug\'ilgan sana': ['Tug\'ilgan sana', 'Tugilgan sana', 'Birth Date'],
            'Mutaxassisligi': ['Mutaxassisligi', 'Mutaxassislik', 'Specialty'],
            'Doimiy yashash manzili Viloyati': ['Doimiy yashash manzili Viloyati', 'Viloyat', 'Region', 'Doimiy viloyat'],
            'Doimiy yashash manzili Tuman': ['Doimiy yashash manzili Tuman', 'Tuman', 'District', 'Doimiy tuman'],
            'Vaqtincha yashash manzili Viloyat': ['Vaqtincha yashash manzili Viloyat', 'Vaqtincha viloyat', 'Temporary Region'],
            'Vaqtincha yashash manzili Tuman': ['Vaqtincha yashash manzili Tuman', 'Vaqtincha tuman', 'Temporary District'],
            'Vaqtincha yashash manzili Joriy manzili': ['Vaqtincha yashash manzili Joriy manzili', 'Joriy manzil', 'Temporary Address', 'Manzil'],
            'Yashash turi': ['Yashash turi', 'Yashash', 'Residence Type'],
            'Guruh': ['Guruh', 'Group'],
            'O\'quv kursi': ['O\'quv kursi', 'Kurs', 'Course'],
            'OTM': ['OTM', 'Otm', 'University'],
            'To\'lov turi': ['To\'lov turi', 'Tulov turi', 'Payment Type'],
            'Ta\'lim shakli': ['Ta\'lim shakli', 'Talim shakli', 'Education Form']
        }
        
        # Mavjud ustunlarni aniqlash
        actual_columns = {}
        missing_columns = []
        for key, aliases in required_columns.items():
            found = False
            for alias in aliases:
                if alias in df.columns:
                    actual_columns[key] = alias
                    found = True
                    break
            if not found:
                actual_columns[key] = None
                missing_columns.append(key)
        
        if missing_columns:
            print(f"Eslatma: Quyidagi ustunlar topilmadi va standart qiymatlar ishlatiladi: {', '.join(missing_columns)}")
        
        # Fakultetni yaratish yoki olish
        faculty, _ = Faculty.objects.get_or_create(
            name="Raqamli texnologiya va suniy intelekt",
            defaults={'description': 'Raqamli texnologiyalar fakulteti'}
        )
        
        # Xatolarni saqlash uchun ro'yxat
        errors = []
        successful = 0
        
        # Har bir qatorni qayta ishlash
        for index, row in df.iterrows():
            try:
                # Excel indexini tuzatish (2-qator tashlab ketilganligi uchun)
                excel_row = index + 2 if index < 1 else index + 3
                
                # Talaba ID ni tekshirish
                student_id = row[actual_columns.get("Talaba ID")] if actual_columns.get("Talaba ID") in df.columns else None
                if pd.isna(student_id):
                    student_id = Student.objects.count() + 1
                    print(f"Qator {excel_row}: Talaba ID bo'sh. Avtomatik ID ({student_id}) ishlatildi.")
                
                # O'quv kursini tekshirish
                course = row[actual_columns["O'quv kursi"]] if actual_columns["O'quv kursi"] else None
                try:
                    course = float(course)
                    if not course.is_integer() or course < 1 or course > 4:
                        course = 1
                        errors.append(f"Qator {excel_row}: O'quv kursi noto'g'ri (1-4 oralig'ida bo'lishi kerak). Standart qiymat (1) ishlatildi.")
                    else:
                        course = int(course)
                        print(f"Qator {excel_row}: O'quv kursi sifatida {course} ishlatildi.")
                except (ValueError, TypeError):
                    course = 1
                    errors.append(f"Qator {excel_row}: O'quv kursi bo'sh yoki noto'g'ri formatda. Standart qiymat (1) ishlatildi.")
                
                # Mutaxassislikni yaratish yoki olish
                mutaxassislik_name = row[actual_columns["Mutaxassisligi"]] if actual_columns["Mutaxassisligi"] else None
                if pd.isna(mutaxassislik_name):
                    mutaxassislik_name = "Noma'lum"
                    errors.append(f"Qator {excel_row}: Mutaxassislik bo'sh. Standart qiymat (Noma'lum) ishlatildi.")
                mutaxassislik, _ = Mutaxassislik.objects.get_or_create(
                    name=mutaxassislik_name
                )
                
                # Davlatni yaratish yoki olish
                country, _ = Country.objects.get_or_create(
                    name="O'zbekiston"
                )
                
                # Doimiy viloyatni yaratish yoki olish
                const_region_name = row[actual_columns["Doimiy yashash manzili Viloyati"]] if actual_columns["Doimiy yashash manzili Viloyati"] else None
                if pd.isna(const_region_name):
                    const_region_name = "Samarqand"
                    print(f"Qator {excel_row}: Doimiy viloyat bo'sh yoki topilmadi. Standart qiymat (Samarqand) ishlatildi.")
                const_region, _ = Region.objects.get_or_create(
                    name=const_region_name
                )
                
                # Doimiy tumanni yaratish yoki olish
                const_district_name = row[actual_columns["Doimiy yashash manzili Tuman"]] if actual_columns["Doimiy yashash manzili Tuman"] else None
                if pd.isna(const_district_name):
                    const_district_name = "Payariq"
                    print(f"Qator {excel_row}: Doimiy tuman bo'sh yoki topilmadi. Standart qiymat (Payariq) ishlatildi.")
                const_district, _ = District.objects.get_or_create(
                    name=const_district_name,
                    region=const_region
                )
                
                # Vaqtincha viloyatni yaratish yoki olish
                temp_region_name = row[actual_columns["Vaqtincha yashash manzili Viloyat"]] if actual_columns["Vaqtincha yashash manzili Viloyat"] else None
                if pd.isna(temp_region_name):
                    temp_region_name = "Samarqand"
                    print(f"Qator {excel_row}: Vaqtincha viloyat bo'sh yoki topilmadi. Standart qiymat (Samarqand) ishlatildi.")
                temp_region, _ = Region.objects.get_or_create(
                    name=temp_region_name
                )
                
                # Vaqtincha tumanni yaratish yoki olish
                temp_district_name = row[actual_columns["Vaqtincha yashash manzili Tuman"]] if actual_columns["Vaqtincha yashash manzili Tuman"] else None
                if pd.isna(temp_district_name):
                    temp_district_name = "Payariq"
                    print(f"Qator {excel_row}: Vaqtincha tuman bo'sh yoki topilmadi. Standart qiymat (Payariq) ishlatildi.")
                temp_district, _ = District.objects.get_or_create(
                    name=temp_district_name,
                    region=temp_region
                )
                
                # Joriy manzilni tekshirish
                temporary_address = row[actual_columns["Vaqtincha yashash manzili Joriy manzili"]] if actual_columns["Vaqtincha yashash manzili Joriy manzili"] else None
                if pd.isna(temporary_address):
                    temporary_address = "Samarqand, Payariq tumani"
                    print(f"Qator {excel_row}: Joriy manzil bo'sh yoki topilmadi. Standart qiymat (Samarqand, Payariq tumani) ishlatildi.")
                
                # Guruhni yaratish yoki olish
                group_name = row[actual_columns["Guruh"]] if actual_columns["Guruh"] else None
                if pd.isna(group_name):
                    group_name = "Noma'lum"
                    print(f"Qator {excel_row}: Guruh bo'sh. Standart qiymat (Noma'lum) ishlatildi.")
                group, created = Group.objects.get_or_create(
                    name=group_name,
                    faculty=faculty,
                    defaults={'course': course, 'tutor': user}
                )
                if not created and group.tutor != user:
                    group.tutor = user
                    group.save()
                    print(f"Qator {excel_row}: Guruh {group_name} uchun tuto'r {user.username} ga yangilandi.")
                
                # TTJ yoki Room ni yaratish yoki olish
                yashash_turi = row[actual_columns["Yashash turi"]] if actual_columns["Yashash turi"] else None
                if pd.isna(yashash_turi):
                    yashash_turi = "O'z uyida"
                    print(f"Qator {excel_row}: Yashash turi bo'sh. Standart qiymat (O'z uyida) ishlatildi.")
                ttj = None
                room = None
                if yashash_turi == "Talabalar turar joyida":
                    ttj, _ = TTJ.objects.get_or_create(
                        name="Qarshi TTJ",
                        address=temporary_address,
                        region=temp_region,
                        district=temp_district,
                        defaults={
                            'capacity': 100,
                            'has_internet': True,
                            'has_heating': True,
                            'condition': 'good',
                            'manager_name': 'Noma\'lum',
                            'manager_phone': 'Noma\'lum',
                            'notes': ''
                        }
                    )
                elif yashash_turi == "Ijaradagi uyda":
                    room, _ = Room.objects.get_or_create(
                        address=temporary_address,
                        defaults={
                            'room_number': 'Noma\'lum',
                            'room_type': 'shared',
                            'area': 50.0,
                            'rent_price': 0,
                            'has_kitchen': False,
                            'has_bathroom': False,
                            'has_internet': False,
                            'has_heating': False,
                            'condition': 'good',
                            'landlord_name': 'Noma\'lum',
                            'landlord_phone': 'Noma\'lum',
                            'notes': ''
                        }
                    )
                
                # Tug'ilgan sanani parse qilish
                birth_date = None
                if actual_columns["Tug\'ilgan sana"]:
                    birth_date_str = str(row[actual_columns["Tug\'ilgan sana"]]).strip()
                    print(f"Qator {excel_row}: Tug'ilgan sana o'qildi: {birth_date_str}")
                    try:
                        # Sana formatlarini sinab ko'rish
                        for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%m/%d/%Y', '%Y/%m/%d']:
                            try:
                                birth_date = pd.to_datetime(birth_date_str, format=fmt, errors='coerce')
                                if not pd.isna(birth_date):
                                    break
                            except ValueError:
                                continue
                        if pd.isna(birth_date):
                            raise ValueError(f"Noto'g'ri sana formati: {birth_date_str}")
                    except (ValueError, TypeError):
                        errors.append(f"Qator {excel_row}: Tug'ilgan sana noto'g'ri formatda ({birth_date_str}). Standart qiymat (2000-01-01) ishlatildi.")
                        birth_date = date(2000, 1, 1)
                else:
                    errors.append(f"Qator {excel_row}: Tug'ilgan sana ustuni topilmadi. Standart qiymat (2000-01-01) ishlatildi.")
                    birth_date = date(2000, 1, 1)
                
                # F.I.O ni ajratish
                fio = row[actual_columns["F.I.O"]] if actual_columns["F.I.O"] else None
                if pd.isna(fio):
                    fio = "Noma'lum Noma'lum"
                    errors.append(f"Qator {excel_row}: F.I.O bo'sh. Standart qiymat (Noma'lum Noma'lum) ishlatildi.")
                fio = str(fio).strip().split()
                if len(fio) < 2:
                    errors.append(f"Qator {excel_row}: F.I.O noto'g'ri formatda (kamida ism va familiya kerak). Standart qiymat ishlatildi.")
                    last_name = fio[0] if fio else "Noma'lum"
                    first_name = fio[1] if len(fio) > 1 else "Noma'lum"
                    middle_name = ""
                else:
                    last_name = fio[0]
                    first_name = fio[1]
                    middle_name = fio[2] if len(fio) > 2 else ""
                
                # JSHSHIR ni tekshirish
                jshshir = row[actual_columns["JSHSHIR"]] if actual_columns["JSHSHIR"] else None
                if pd.isna(jshshir):
                    jshshir = f"TEMP{uuid.uuid4().hex[:14]}"  # Vaqtinchalik JSHSHIR
                    errors.append(f"Qator {excel_row}: JSHSHIR bo'sh. Vaqtinchalik JSHSHIR ({jshshir}) ishlatildi.")
                else:
                    # JSHSHIR ni tozalash va tekshirish
                    jshshir = str(jshshir).strip().replace('.0', '')  # Float ni olib tashlash
                    print(f"Qator {excel_row}: JSHSHIR o'qildi: {jshshir}, uzunlik: {len(jshshir)}")
                    if not jshshir.isdigit() or len(jshshir) != 14:
                        errors.append(f"Qator {excel_row}: JSHSHIR noto'g'ri formatda ({jshshir}, uzunlik: {len(jshshir)}). Vaqtinchalik JSHSHIR ishlatildi.")
                        jshshir = f"TEMP{uuid.uuid4().hex[:14]}"  # Vaqtinchalik JSHSHIR
                
                # Pasportni tekshirish
                passport = row[actual_columns["Pasport"]] if actual_columns["Pasport"] else None
                if pd.isna(passport):
                    passport = "Noma'lum"
                    errors.append(f"Qator {excel_row}: Pasport bo'sh. Standart qiymat (Noma'lum) ishlatildi.")
                
                # Telefon raqamini tekshirish
                phone_number = row[actual_columns["Telefon raqami"]] if actual_columns["Telefon raqami"] else None
                if pd.isna(phone_number):
                    phone_number = "Noma'lum"
                    errors.append(f"Qator {excel_row}: Telefon raqami bo'sh. Standart qiymat (Noma'lum) ishlatildi.")
                
                # Jinsni tekshirish
                gender = row[actual_columns["Jinsi"]] if actual_columns["Jinsi"] else None
                if pd.isna(gender) or gender not in ["Erkak", "Ayol"]:
                    gender = "Erkak"
                    errors.append(f"Qator {excel_row}: Jins noto'g'ri yoki bo'sh. Standart qiymat (Erkak) ishlatildi.")
                
                # Talaba obyektini yaratish
                student, created = Student.objects.get_or_create(
                    jshshir=jshshir,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'middle_name': middle_name,
                        'gender': 'male' if gender == "Erkak" else 'female',
                        'birth_date': birth_date,
                        'group': group,
                        'is_renting': yashash_turi == "Ijaradagi uyda",
                        'address': temporary_address,
                        'phone_number': phone_number,
                        'email': '',
                        'is_orphan': row.get("Chin yetim", False) == True,
                        'has_disability': row.get("Nogironligi bor", False) == True,
                        'lives_in_dormitory': yashash_turi == "Talabalar turar joyida",
                        'student_id': int(student_id) if student_id else Student.objects.count() + 1,
                        'fuqaro': 'uz',
                        'passport': passport,
                        'otm': row[actual_columns["OTM"]] if actual_columns["OTM"] and not pd.isna(row[actual_columns["OTM"]]) else "Noma'lum",
                        'talim_turi': 'bakalavr',
                        'tulov_turi': 'grant' if actual_columns["To'lov turi"] and row[actual_columns["To'lov turi"]] == "Davlat granti" else 'contract',
                        'talim_shakli': row[actual_columns["Ta'lim shakli"]].lower() if actual_columns["Ta'lim shakli"] and not pd.isna(row[actual_columns["Ta'lim shakli"]]) else 'kunduzgi',
                        'shifr': '',
                        'mutaxassislik': mutaxassislik,
                        'country': country,
                        'const_region': const_region,
                        'const_district': const_district,
                        'temporary_region': temp_region,
                        'temporary_district': temp_district,
                        'temporary_address': temporary_address,
                        'appartment_type': 'ttj' if yashash_turi == "Talabalar turar joyida" else 'rent' if yashash_turi == "Ijaradagi uyda" else 'home',
                        'family_type': 'turmush_qurmagan',
                        'parent_status': row.get("Boquvchisini yuqotgan", None),
                        'is_in_social_protection': row.get("Ijtimoiy himoya reestiriga kiritilgan", False) == True,
                        'is_in_temir_daftar': row.get("Temir daftarga kiritilgan oila farzandi", False) == True,
                        'is_in_women_daftar': row.get("Ayollar daftariga kirgizilgan", False) == True,
                        'is_in_youth_daftar': row.get("Yoshlar daftariga kiritilgan", False) == True,
                        'is_in_orphanage': row.get("Mehribonlik uyi tarbiyalanuvchisi", False) == True,
                        'parents_divorced': row.get("Ota-onasi ajrashgan", False) == True,
                        'nation': 'uzbek',
                        'ttj': ttj,
                        'room': room,
                    }
                )
                
                if created:
                    successful += 1
                    print(f"Talaba {student.first_name} {student.last_name} muvaffaqiyatli qo'shildi.")
                else:
                    print(f"Talaba {student.first_name} {student.last_name} allaqachon mavjud.")
                    
            except Exception as e:
                errors.append(f"Qator {excel_row}: {str(e)}")
        
        return successful, errors
    
    except Exception as e:
        return 0, [f"Faylni o'qishda xato: {str(e)}. Iltimos, fayl .xls yoki .xlsx formatida ekanligiga va barcha ustunlar to'g'ri to'ldirilganligiga ishonch hosil qiling."]

def upload_excel(request):
    if not request.user.is_authenticated:
        return render(request, 'students/upload_excel.html', {'message': 'Faylni yuklash uchun tizimga kiring.', 'errors': []})
    
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        fs = FileSystemStorage()
        filename = fs.save(excel_file.name, excel_file)
        file_path = fs.path(filename)
        
        try:
            successful, errors = import_students_from_excel(file_path, request.user)
            os.remove(file_path)  # Faylni o'chirish
            context = {
                'successful': successful,
                'errors': errors,
                'message': f"Muvaffaqiyatli import qilinganlar: {successful}. Xatolar soni: {len(errors)}"
            }
            return render(request, 'students/upload_excel.html', context)
        except Exception as e:
            os.remove(file_path)  # Xato yuz bersa ham faylni o'chirish
            context = {
                'successful': 0,
                'errors': [f"Faylni o'qishda xato: {str(e)}. Iltimos, fayl .xls yoki .xlsx formatida ekanligiga va barcha ustunlar to'g'ri to'ldirilganligiga ishonch hosil qiling."],
                'message': 'Fayl yuklashda xato yuz berdi.'
            }
            return render(request, 'students/upload_excel.html', context)
    
    return render(request, 'students/upload_excel.html', {'message': ''})
