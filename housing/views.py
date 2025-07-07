from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.forms import modelformset_factory
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import HousingInspection, InspectionPhoto, Room
from .forms import HousingInspectionForm, InspectionPhotoForm,RoomForm
from students.models import Student
from accounts.decorators import tutor_required, dean_required


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Room, HousingInspection, InspectionPhoto
from students.models import Student
from accounts.models import User

@login_required
def room_list(request):
    """Tutor uchun o'z guruh talabalarining xonalari ro'yxati"""
    if not request.user.is_tutor():
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('dashboard')
    
    # Tutorga biriktirilgan guruhlar
    tutor_groups = request.user.assigned_groups.all()
    
    # Bu guruhlardagi talabalar (faqat ijara xonadonida yashaydiganlar)
    students = Student.objects.filter(
        group__in=tutor_groups, 
        is_renting=True,
        room__isnull=False  # Xonasi bo'lgan talabalar
    ).select_related('room', 'group')
    
    # Xonalar bo'yicha guruhlash
    rooms_dict = {}
    for student in students:
        room = student.room
        if room.id not in rooms_dict:
            # Har bir xona uchun tekshirish statusini aniqlash
            last_inspection = room.inspections.order_by('-inspection_date').first()
            
            status = 'pending'
            status_class = 'warning'
            if last_inspection:
                days_since = (timezone.now().date() - last_inspection.inspection_date.date()).days
                if days_since <= 30:
                    status = 'inspected'
                    status_class = 'success'
                else:
                    status = 'overdue'
                    status_class = 'danger'
            
            rooms_dict[room.id] = {
                'room': room,
                'students': [],
                'status': status,
                'status_class': status_class,
                'last_inspection': last_inspection
            }
        
        rooms_dict[room.id]['students'].append(student)
    
    # Qidiruv
    search = request.GET.get('search')
    if search:
        filtered_rooms = {}
        for room_id, room_data in rooms_dict.items():
            room = room_data['room']
            students_in_room = room_data['students']
            
            # Xona manzili yoki talaba ismi bo'yicha qidirish
            if (search.lower() in room.address.lower() or 
                search.lower() in room.room_number.lower() or
                search.lower() in room.landlord_name.lower() or
                any(search.lower() in student.full_name.lower() for student in students_in_room)):
                filtered_rooms[room_id] = room_data
        
        rooms_dict = filtered_rooms
    
    # List formatiga o'tkazish
    rooms_with_students = list(rooms_dict.values())
    
    # Pagination
    paginator = Paginator(rooms_with_students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'rooms_with_students': page_obj,  # Bu nom muhim!
        'page_obj': page_obj,
        'search': search,
        'total_rooms': len(rooms_with_students)
    }
    return render(request, 'housing/room_list.html', context)
@login_required
def room_detail(request, room_id):
    """Xona tafsilotlari"""
    room = get_object_or_404(Room, id=room_id)
    
    # Faqat tutor o'z guruh talabalarining xonasini ko'ra oladi
    if request.user.is_tutor():
        tutor_groups = request.user.assigned_groups.all()
        room_students = room.students.filter(group__in=tutor_groups)
        if not room_students.exists():
            messages.error(request, "Bu xonaga kirish huquqingiz yo'q!")
            return redirect('room_list')
    else:
        room_students = room.students.all()
    
    # Oxirgi tekshiruvlar
    inspections = room.inspections.order_by('-inspection_date')[:5]
    
    context = {
        'room': room,
        'students': room_students,
        'inspections': inspections,
        'inspection_status': room.inspection_status,
        'inspection_badge': room.inspection_badge
    }
    return render(request, 'housing/room_detail.html', context)

@login_required
def create_inspection(request, room_id):
    """Yangi tekshiruv yaratish"""
    room = get_object_or_404(Room, id=room_id)
    
    if not request.user.is_tutor():
        messages.error(request, "Faqat tutorlar tekshiruv o'tkazishi mumkin!")
        return redirect('room_detail', room_id=room_id)
    
    if request.method == 'POST':
        # Tekshiruv ma'lumotlarini olish
        condition = request.POST.get('condition')
        comment = request.POST.get('comment')
        
        # Validate required fields
        if not condition:
            messages.error(request, "Yashash sharoiti holatini tanlang!")
            return redirect('create_inspection', room_id=room_id)
        
        if not comment or len(comment.strip()) < 10:
            messages.error(request, "Izoh kamida 10 ta belgidan iborat bo'lishi kerak!")
            return redirect('create_inspection', room_id=room_id)
        
        # Xonadagi birinchi tal Aa olish (tekshiruv uchun)
        student = room.current_residents.first()
        if not student:
            messages.error(request, "Bu xonada talaba topilmadi!")
            return redirect('room_detail', room_id=room_id)
        
        # Tekshiruv yaratish
        inspection = HousingInspection.objects.create(
            student=student,
            room=room,
            inspector=request.user,
            condition=condition,
            comment=comment,
            cleanliness_score=int(request.POST.get('cleanliness_score', 5)),
            safety_score=int(request.POST.get('safety_score', 5)),
            comfort_score=int(request.POST.get('comfort_score', 5))
        )
        
        # Rasmlar va ularning izohlarini saqlash
        photos = request.FILES.getlist('photos')
        photo_comments = [
            request.POST.get('photo_comment_1', ''),
            request.POST.get('photo_comment_2', ''),
            request.POST.get('photo_comment_3', '')
        ]
        
        # Validate at least one photo is uploaded
        if not photos:
            inspection.delete()  # Rollback inspection if no photos
            messages.error(request, "Kamida bitta rasm yuklash kerak!")
            return redirect('create_inspection', room_id=room_id)
        
        # Save photos with corresponding captions
        for i, photo in enumerate(photos[:3]):  # Limit to 3 photos to match form
            if photo.size > 5 * 1024 * 1024:  # Validate file size (5MB)
                inspection.delete()
                messages.error(request, f"Rasm {i+1} hajmi 5MB dan oshmasligi kerak!")
                return redirect('create_inspection', room_id=room_id)
            
            if not photo.content_type.startswith('image/'):
                inspection.delete()
                messages.error(request, f"Rasm {i+1} faqat rasm formatida bo'lishi kerak!")
                return redirect('create_inspection', room_id=room_id)
            
            InspectionPhoto.objects.create(
                inspection=inspection,
                photo=photo,
                caption=photo_comments[i]
            )
        
        messages.success(request, "Tekshiruv muvaffaqiyatli yaratildi!")
        return redirect('room_detail', room_id=room_id)
    
    context = {
        'room': room,
        'students': room.current_residents.all()
    }
    return render(request, 'housing/create_inspection.html', context)

@login_required
def dean_inspections(request):
    """Dekan uchun tekshiruvlarni ko'rish va tasdiqlash"""
    if not request.user.is_dean():
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('dashboard')
    
    # Dekan fakultetidagi tekshiruvlar
    faculty = request.user.faculty
    inspections = HousingInspection.objects.filter(
        student__group__faculty=faculty
    ).order_by('-inspection_date')
    
    # Status bo'yicha filtrlash
    status = request.GET.get('status')
    if status:
        inspections = inspections.filter(status=status)
    
    # Pagination
    paginator = Paginator(inspections, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status': status
    }
    return render(request, 'housing/dean_inspections.html', context)

@login_required
def approve_inspection(request, inspection_id):
    """Tekshiruvni tasdiqlash/bekor qilish"""
    if not request.user.is_dean():
        return JsonResponse({'error': 'Ruxsat yo\'q'}, status=403)
    
    inspection = get_object_or_404(HousingInspection, id=inspection_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        dean_comment = request.POST.get('dean_comment', '')
        
        if action == 'approve':
            inspection.status = 'approved'
        elif action == 'reject':
            inspection.status = 'rejected'
        
        inspection.dean_comment = dean_comment
        inspection.reviewed_by = request.user
        inspection.reviewed_at = timezone.now()
        inspection.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@dean_required
def review_inspection(request, pk):
    inspection = get_object_or_404(
        HousingInspection, 
        pk=pk, 
        student__group__faculty=request.user.faculty,
        status='pending'
    )
    
    if request.method == 'POST':
        status = request.POST.get('status')
        comment = request.POST.get('dean_comment', '')
        
        if status in ['approved', 'rejected']:
            inspection.status = status
            inspection.dean_comment = comment
            inspection.reviewed_by = request.user
            inspection.reviewed_at = timezone.now()
            inspection.save()
            
            status_text = 'tasdiqlandi' if status == 'approved' else 'rad etildi'
            messages.success(request, f'Tekshirish {status_text}.')
            return redirect('dean_dashboard')
    
    context = {
        'inspection': inspection,
    }
    return render(request, 'housing/review_inspection.html', context)


@login_required
def inspection_detail(request, pk):
    user = request.user
    
    if user.is_rector():
        inspection = get_object_or_404(HousingInspection, pk=pk)
    elif user.is_dean():
        inspection = get_object_or_404(HousingInspection, pk=pk, student__group__faculty=user.faculty)
    elif user.is_tutor():
        inspection = get_object_or_404(HousingInspection, pk=pk, inspector=user)
    else:
        return redirect('dashboard')
    
    context = {
        'inspection': inspection,
    }
    return render(request, 'housing/inspection_detail.html', context)


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import HousingInspection
from students.models import Student
from faculty.models import Faculty
import logging

logger = logging.getLogger(__name__)

@login_required
def inspection_list(request):
    user = request.user
    housing_inspections = HousingInspection.objects.none()  # Start with empty queryset

    if user.is_tutor():
        # Tutors see inspections where they are the inspector
        housing_inspections = HousingInspection.objects.filter(
            inspector=user
        ).select_related('student', 'room', 'inspector', 'reviewed_by')

    elif user.is_dean():
        # Deans see inspections for students in their faculty (or fallback)
        if user.faculty:
            try:
                # Try filtering by Student.faculty (ForeignKey)
                housing_inspections = HousingInspection.objects.filter(
                    student__faculty=user.faculty
                ).select_related('student', 'room', 'inspector', 'reviewed_by')
            except Exception as e:
                logger.error(f"Error filtering by faculty: {e}")
                # Fallback: If Student.faculty is missing or misconfigured
                # Option 1: Show all pending inspections for deans to review
                housing_inspections = HousingInspection.objects.filter(
                    status='pending'
                ).select_related('student', 'room', 'inspector', 'reviewed_by')
                logger.info("Falling back to pending inspections for dean")
        else:
            # If dean has no faculty assigned, show pending inspections
            housing_inspections = HousingInspection.objects.filter(
                status='pending'
            ).select_related('student', 'room', 'inspector', 'reviewed_by')
            logger.info("No faculty assigned to dean, showing pending inspections")

    elif user.is_rector():
        # Rectors see all inspections
        housing_inspections = HousingInspection.objects.all().select_related(
            'student', 'room', 'inspector', 'reviewed_by'
        )

    logger.info(f"User: {user}, Type: {user.user_type}, Faculty: {user.faculty}, Inspections: {housing_inspections.count()}")
    context = {'housing_inspections': housing_inspections}
    return render(request, 'housing/inspection_list.html', context)
@dean_required
def pending_inspections(request):
    inspections = HousingInspection.objects.filter(
        student__group__faculty=request.user.faculty,
        status='pending'
    ).order_by('-inspection_date')
    
    context = {
        'inspections': inspections,
    }
    return render(request, 'housing/pending_inspections.html', context)

from django.shortcuts import render, get_object_or_404
from .models import HousingInspection, InspectionPhoto

@login_required
def inspection_photos(request, pk):
    inspection = get_object_or_404(HousingInspection, pk=pk)
    photos = inspection.photos.all()
    context = {
        'inspection': inspection,
        'photos': photos
    }
    return render(request, 'housing/inspection_photos.html', context)
    

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import RoomForm

@login_required
def room_create(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        print("Submitted data:", request.POST)  # Debug
        print("Form errors:", form.errors)  # Debug
        if form.is_valid():
            room = form.save()
            messages.success(request, f"{room} muvaffaqiyatli qo'shildi.")
            return_to = request.session.get('return_to', 'student_create')
            student_pk = request.session.get('student_pk')
            # Update session data to select the new room
            if 'student_form_data' in request.session:
                request.session['student_form_data']['room'] = str(room.id)
            if return_to == 'student_edit' and student_pk:
                return redirect('student_edit', pk=student_pk)
            return redirect('student_create')
        else:
            messages.error(request, "Xona qo'shishda xatolik yuz berdi. Iltimos, ma'lumotlarni tekshiring.")
            # Log specific field errors for better feedback
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RoomForm()
    
    context = {
        'form': form,
        'title': 'Yangi xona qo‘shish',
        'return_to': request.session.get('return_to'),
        'student_pk': request.session.get('student_pk'),
    }
    return render(request, 'housing/room_form.html', context)

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from students.models import Student
from housing.models import Room

class TutorRentalHousingListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Room
    template_name = 'housing/room_list.html'
    context_object_name = 'rooms'
    
    def test_func(self):
        return self.request.user.is_tutor()
    
    def get_queryset(self):
        # Get all students in the tutor's assigned groups
        tutor_groups = self.request.user.assigned_groups.all()
        student_ids = Student.objects.filter(group__in=tutor_groups, is_renting=True).values_list('id', flat=True)
        
        # Get rooms where these students live
        return Room.objects.filter(students__id__in=student_ids).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add additional context about students in each room
        rooms_with_students = []
        for room in context['rooms']:
            students = Student.objects.filter(
                group__in=self.request.user.assigned_groups.all(),
                room=room
            )
            rooms_with_students.append({
                'room': room,
                'students': students,
                'students_count': students.count()
            })
        
        context['rooms_with_students'] = rooms_with_students
        return context