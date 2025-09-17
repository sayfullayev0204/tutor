from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from datetime import date
from .models import User, Group, Student, Attendance, AttendanceRecord
from faculty.models import Faculty


@login_required
def dashboard(request):
    context = {
        'user': request.user,
        'current_date': date.today()
    }
    return render(request, 'attendance/dashboard.html', context)

@login_required
def attendance_view(request):
    user = request.user
    context = {'user': user, 'current_date': date.today()}
    
    if user.user_type == 'tutor':
        groups = Group.objects.filter(tutor=user)
        groups_with_status = []
        
        for group in groups:
            today_attendance = Attendance.objects.filter(
                group=group, 
                date=date.today()
            ).first()
            
            status = 'taken' if today_attendance else 'pending'
            groups_with_status.append({
                'group': group,
                'status': status,
                'attendance': today_attendance
            })
        
        context['groups_with_status'] = groups_with_status
        return render(request, 'attendance/tutor_attendance.html', context)
    
    elif user.user_type == 'dean':
        try:
            faculty = Faculty.objects.get(dean=user)
            groups = Group.objects.filter(faculty=faculty)
            groups_with_status = []
            
            for group in groups:
                today_attendance = Attendance.objects.filter(
                    group=group, 
                    date=date.today()
                ).first()
                
                status = 'taken' if today_attendance else 'pending'
                groups_with_status.append({
                    'group': group,
                    'status': status,
                    'attendance': today_attendance
                })
            
            context['faculty'] = faculty
            context['groups_with_status'] = groups_with_status
            return render(request, 'attendance/dean_attendance.html', context)
        except Faculty.DoesNotExist:
            messages.error(request, 'Faculty not found for this dean.')
            return redirect('dashboard')
    
    elif user.user_type == 'rector':
        faculties = Faculty.objects.all()
        faculties_with_stats = []
        
        for faculty in faculties:
            groups = Group.objects.filter(faculty=faculty)
            total_groups = groups.count()
            taken_today = Attendance.objects.filter(
                group__faculty=faculty,
                date=date.today()
            ).count()
            
            faculties_with_stats.append({
                'faculty': faculty,
                'total_groups': total_groups,
                'taken_today': taken_today,
                'pending': total_groups - taken_today
            })
        
        context['faculties_with_stats'] = faculties_with_stats
        return render(request, 'attendance/rector_attendance.html', context)
    
    return redirect('dashboard')

@login_required
def take_attendance(request, group_id):
    if request.user.user_type != 'tutor':
        messages.error(request, 'Only tutors can take attendance.')
        return redirect('attendance_view')
    
    group = get_object_or_404(Group, id=group_id, tutor=request.user)
    
    existing_attendance = Attendance.objects.filter(
        group=group, 
        date=date.today()
    ).first()
    
    if existing_attendance and existing_attendance.is_locked:
        messages.error(request, 'Attendance for today has already been taken and cannot be modified.')
        return redirect('attendance_view')
    
    students = Student.objects.filter(group=group).order_by('first_name', 'last_name')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                attendance, created = Attendance.objects.get_or_create(
                    group=group,
                    date=date.today(),
                    defaults={'taken_by': request.user}
                )
                
                if not created:
                    AttendanceRecord.objects.filter(attendance=attendance).delete()
                
                for student in students:
                    is_present = request.POST.get(f'student_{student.id}') == 'on'
                    note = request.POST.get(f'note_{student.id}', '')
                    
                    AttendanceRecord.objects.create(
                        attendance=attendance,
                        student=student,
                        is_present=is_present,
                        note=note
                    )
                
                attendance.is_locked = True
                attendance.save()
                
                messages.success(request, f'Attendance for {group.name} has been saved successfully.')
                return redirect('attendance_view')
                
        except Exception as e:
            messages.error(request, f'Error saving attendance: {str(e)}')
    
    attendance_records = {}
    if existing_attendance:
        records = AttendanceRecord.objects.filter(attendance=existing_attendance)
        attendance_records = {record.student.id: record for record in records}
    
    context = {
        'group': group,
        'students': students,
        'attendance_records': attendance_records,
        'existing_attendance': existing_attendance,
        'current_date': date.today()
    }
    
    return render(request, 'attendance/take_attendance.html', context)

@login_required
def faculty_groups(request, faculty_id):
    if request.user.user_type != 'rector':
        messages.error(request, 'Access denied.')
        return redirect('attendance_view')
    
    faculty = get_object_or_404(Faculty, id=faculty_id)
    groups = Group.objects.filter(faculty=faculty)
    groups_with_status = []
    
    for group in groups:
        today_attendance = Attendance.objects.filter(
            group=group, 
            date=date.today()
        ).first()
        
        status = 'taken' if today_attendance else 'pending'
        groups_with_status.append({
            'group': group,
            'status': status,
            'attendance': today_attendance
        })
    
    context = {
        'faculty': faculty,
        'groups_with_status': groups_with_status,
        'current_date': date.today()
    }
    
    return render(request, 'attendance/faculty_groups.html', context)

@login_required
def attendance_details(request, group_id, attendance_date=None):
    """View attendance details for a specific group and date"""
    user = request.user
    group = get_object_or_404(Group, id=group_id)
    
    # Check permissions
    if user.user_type == 'tutor' and group.tutor != user:
        messages.error(request, 'You can only view attendance for your own groups.')
        return redirect('attendance_view')
    elif user.user_type == 'dean':
        try:
            faculty = Faculty.objects.get(dean=user)
            if group.faculty != faculty:
                messages.error(request, 'You can only view attendance for groups in your faculty.')
                return redirect('attendance_view')
        except Faculty.DoesNotExist:
            messages.error(request, 'Faculty not found.')
            return redirect('attendance_view')
    elif user.user_type not in ['tutor', 'dean', 'rector']:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    # Get attendance date
    if attendance_date:
        try:
            from datetime import datetime
            target_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        except ValueError:
            target_date = date.today()
    else:
        target_date = date.today()
    
    # Get attendance record
    attendance = get_object_or_404(Attendance, group=group, date=target_date)
    
    # Get all attendance records for this attendance
    attendance_records = AttendanceRecord.objects.filter(
        attendance=attendance
    ).select_related('student').order_by('student__first_name', 'student__last_name')
    
    # Separate present and absent students
    present_students = []
    absent_students = []
    
    for record in attendance_records:
        if record.is_present:
            present_students.append(record)
        else:
            absent_students.append(record)
    
    # Calculate statistics
    total_students = attendance_records.count()
    present_count = len(present_students)
    absent_count = len(absent_students)
    attendance_percentage = (present_count / total_students * 100) if total_students > 0 else 0
    
    context = {
        'group': group,
        'attendance': attendance,
        'attendance_date': target_date,
        'present_students': present_students,
        'absent_students': absent_students,
        'total_students': total_students,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_percentage': round(attendance_percentage, 1),
        'user': user
    }
    
    return render(request, 'attendance/attendance_details.html', context)
