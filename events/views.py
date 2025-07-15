from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Event, EventPhoto

@login_required
def event_list(request):
    """Tutor uchun o'z tadbirlari ro'yxati"""
    if not request.user.is_tutor():
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('dashboard')
    
    # Tutorning tadbirlari
    events = Event.objects.filter(organizer=request.user).order_by('-event_date')
    
    # Qidiruv
    search = request.GET.get('search')
    if search:
        events = events.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search)
        )
    
    # Status bo'yicha filtrlash
    status = request.GET.get('status')
    if status:
        events = events.filter(status=status)
    
    # Pagination
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistika
    stats = {
        'total': events.count(),
        'pending': events.filter(status='pending').count(),
        'approved': events.filter(status='approved').count(),
        'rejected': events.filter(status='rejected').count(),
    }
    
    context = {
        'events': page_obj,
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'stats': stats
    }
    return render(request, 'events/event_list.html', context)

@login_required
def create_event(request):
    """Yangi tadbir yaratish"""
    if not request.user.is_tutor():
        messages.error(request, "Faqat tutorlar tadbir yaratishi mumkin!")
        return redirect('events:event_list')
    
    if request.method == 'POST':
        try:
            # Tadbir ma'lumotlarini olish
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            category = request.POST.get('category')
            event_date = request.POST.get('event_date')
            location = request.POST.get('location', '').strip()
            participants_count = request.POST.get('participants_count')
            
            # Validatsiya
            if not title:
                messages.error(request, "Tadbir nomini kiriting!")
                return render(request, 'events/create_event.html')
            
            if not description:
                messages.error(request, "Tadbir haqida ma'lumot kiriting!")
                return render(request, 'events/create_event.html')
            
            if not event_date:
                messages.error(request, "Tadbir sanasini tanlang!")
                return render(request, 'events/create_event.html')
            
            if not location:
                messages.error(request, "Tadbir o'tkazilgan joyni kiriting!")
                return render(request, 'events/create_event.html')
            
            if not participants_count or int(participants_count) < 1:
                messages.error(request, "Ishtirokchilar sonini kiriting!")
                return render(request, 'events/create_event.html')
            
            # Rasmlar tekshiruvi
            photos = request.FILES.getlist('photos')
            if not photos:
                messages.error(request, "Kamida bitta rasm yuklang!")
                return render(request, 'events/create_event.html')
            
            if len(photos) > 10:
                messages.error(request, "Maksimal 10 ta rasm yuklash mumkin!")
                return render(request, 'events/create_event.html')
            
            # Tadbir yaratish
            event = Event.objects.create(
                title=title,
                description=description,
                category=category,
                event_date=event_date,
                location=location,
                organizer=request.user,
                participants_count=int(participants_count)
            )
            
            # Rasmlarni saqlash
            photo_captions = request.POST.getlist('photo_captions')
            for i, photo in enumerate(photos):
                caption = photo_captions[i] if i < len(photo_captions) else f'Tadbir rasmi {i+1}'
                EventPhoto.objects.create(
                    event=event,
                    photo=photo,
                    caption=caption.strip() or f'Tadbir rasmi {i+1}'
                )
            
            messages.success(request, f"Tadbir muvaffaqiyatli yaratildi! {len(photos)} ta rasm yuklandi. Dekan tomonidan ko'rib chiqilishini kuting.")
            return redirect('events:event_detail', event_id=event.id)
            
        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
    
    return render(request, 'events/create_event.html')

@login_required
def event_detail(request, event_id):
    """Tadbir tafsilotlari"""
    event = get_object_or_404(Event, id=event_id)
    
    # Faqat tutor o'z tadbirini yoki dekan fakultet tadbirlarini ko'ra oladi
    if request.user.is_tutor():
        if event.organizer != request.user:
            messages.error(request, "Bu tadbirga kirish huquqingiz yo'q!")
            return redirect('events:event_list')
    elif request.user.is_dean():
        # Dekan o'z fakultetidagi tadbirlarni ko'ra oladi
        if event.organizer.faculty != request.user.faculty:
            messages.error(request, "Bu tadbirga kirish huquqingiz yo'q!")
            return redirect('events:dean_events')
    else:
        messages.error(request, "Bu sahifaga kirish huquqingiz yo'q!")
        return redirect('dashboard')
    
    context = {
        'event': event,
        'photos': event.photos.all()
    }
    return render(request, 'events/event_detail.html', context)

@login_required
def dean_events(request):
    """Dekan uchun fakultet tadbirlarini ko'rish va tasdiqlash"""
    if not request.user.is_dean():
        messages.error(request, "Sizda bu sahifaga kirish huquqi yo'q!")
        return redirect('dashboard')
    
    # Dekan fakultetidagi tadbirlar
    faculty = request.user.faculty
    events = Event.objects.filter(
        organizer__faculty=faculty
    ).select_related('organizer', 'reviewed_by').order_by('-event_date')
    
    # Status bo'yicha filtrlash
    status = request.GET.get('status')
    if status:
        events = events.filter(status=status)
    
    # Pagination
    paginator = Paginator(events, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'events': page_obj,
        'page_obj': page_obj,
        'status': status
    }
    return render(request, 'events/dean_events.html', context)

@login_required
def approve_event(request, event_id):
    """Tadbirni tasdiqlash/bekor qilish"""
    if not request.user.is_dean():
        return JsonResponse({'error': 'Ruxsat yo\'q'}, status=403)
    
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        dean_comment = request.POST.get('dean_comment', '').strip()
        
        if action == 'approve':
            event.status = 'approved'
            message = 'Tadbir tasdiqlandi!'
        elif action == 'reject':
            event.status = 'rejected'
            message = 'Tadbir rad etildi!'
        else:
            return JsonResponse({'error': 'Noto\'g\'ri amal'}, status=400)
        
        event.dean_comment = dean_comment
        event.reviewed_by = request.user
        event.reviewed_at = timezone.now()
        event.save()
        
        # Success message
        messages.success(request, message)
        
        return JsonResponse({
            'success': True, 
            'message': message,
            'status': event.status
        })
    
    return JsonResponse({'error': 'Noto\'g\'ri so\'rov'}, status=400)

@login_required
def event_details_modal(request, event_id):
    """Tadbir tafsilotlari (AJAX uchun)"""
    event = get_object_or_404(Event, id=event_id)
    
    context = {
        'event': event,
        'photos': event.photos.all()
    }
    
    # AJAX so'rov bo'lsa JSON qaytarish
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.template.loader import render_to_string
        html = render_to_string('events/event_detail_modal.html', context)
        return JsonResponse({'html': html})
    
    return JsonResponse({'error': 'Faqat AJAX so\'rov'}, status=400)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Message, MessageReply
from .forms import MessageForm, MessageReplyForm
from django.utils.translation import gettext_lazy as _
from django.db import models
@login_required
def create_message(request):
    if not (request.user.is_rector() or request.user.is_tutor()):
        messages.error(request, _("Faqat rektor yoki tutor xabar yuborishi mumkin."))
        return redirect('home')  # Adjust 'home' to your actual home URL

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            if request.user.is_tutor():
                message.faculty = None  # Tutors send messages to rector, no faculty
            message.save()
            messages.success(request, _("Xabar muvaffaqiyatli yuborildi."))
            return redirect('message_list')
    else:
        form = MessageForm(user=request.user)
    
    return render(request, 'messages/send_message.html', {'form': form})


@login_required
def message_list(request):
    if request.user.is_rector():
        # Rectors see messages they sent and messages from tutors (faculty is null)
        messages_list = Message.objects.filter(
            models.Q(sender=request.user) | models.Q(faculty__isnull=True)
        ).order_by('-created_at')
    elif request.user.is_dean():
        if not request.user.faculty:
            messages.error(request, _("Sizga fakultet biriktirilmagan. Xabarlarni ko'rish uchun fakultet biriktirilishi kerak."))
            return redirect('home')
        messages_list = Message.objects.filter(faculty=request.user.faculty).order_by('-created_at')
    elif request.user.is_tutor():
        # Tutors see only messages they sent
        messages_list = Message.objects.filter(sender=request.user).order_by('-created_at')
    else:
        messages.error(request, _("Sizda xabarlarni ko'rish huquqi yo'q."))
        return redirect('home')

    return render(request, 'messages/message_list.html', {'messages_list': messages_list})
    
@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    # Access control
    if not (
        request.user.is_rector() or 
        (request.user.is_dean() and request.user.faculty == message.faculty) or 
        (request.user.is_tutor() and request.user == message.sender)
    ):
        messages.error(request, _("Sizda ushbu xabarni ko'rish huquqi yo'q."))
        return redirect('message_list')
    
    # Mark as read for deans or rectors viewing relevant messages
    if (request.user.is_dean() and message.status == 'pending' and request.user.faculty == message.faculty) or \
       (request.user.is_rector() and message.status == 'pending' and message.faculty is None):
        message.status = 'read'
        message.save()
    
    # Handle replies (only deans and rectors can reply)
    if request.method == 'POST' and (request.user.is_dean() or request.user.is_rector()):
        form = MessageReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.sender = request.user
            reply.message = message
            reply.save()
            message.status = 'replied'
            message.save()
            messages.success(request, _("Javob muvaffaqiyatli yuborildi."))
            return redirect('message_detail', message_id=message.id)
    else:
        form = MessageReplyForm()
    
    return render(request, 'messages/message_detail.html', {
        'message': message,
        'form': form,
    })