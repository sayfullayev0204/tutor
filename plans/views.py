from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Plan, Reminder
from .forms import PlanForm, ReminderForm
from accounts.decorators import tutor_required


@tutor_required
def plan_list(request):
    plans = Plan.objects.filter(tutor=request.user)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        plans = plans.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        plans = plans.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(plans, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_plans = Plan.objects.filter(tutor=request.user).count()
    pending_plans = Plan.objects.filter(tutor=request.user, status='pending').count()
    completed_plans = Plan.objects.filter(tutor=request.user, status='completed').count()
    overdue_plans = Plan.objects.filter(
        tutor=request.user,
        due_date__lt=timezone.now(),
        status__in=['pending', 'in_progress']
    ).count()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_plans': total_plans,
        'pending_plans': pending_plans,
        'completed_plans': completed_plans,
        'overdue_plans': overdue_plans,
    }
    return render(request, 'plans/plan_list.html', context)


@tutor_required
def plan_detail(request, pk):
    plan = get_object_or_404(Plan, pk=pk, tutor=request.user)
    reminders = plan.reminders.all().order_by('remind_at')
    
    context = {
        'plan': plan,
        'reminders': reminders,
    }
    return render(request, 'plans/plan_detail.html', context)


@tutor_required
def plan_create(request):
    if request.method == 'POST':
        form = PlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.tutor = request.user
            plan.save()
            messages.success(request, f'Reja "{plan.title}" muvaffaqiyatli yaratildi.')
            return redirect('plan_list')
    else:
        form = PlanForm()
    
    context = {
        'form': form,
        'title': 'Yangi reja yaratish',
    }
    return render(request, 'plans/plan_form.html', context)


@tutor_required
def plan_edit(request, pk):
    plan = get_object_or_404(Plan, pk=pk, tutor=request.user)
    
    if request.method == 'POST':
        form = PlanForm(request.POST, instance=plan)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Reja "{plan.title}" muvaffaqiyatli yangilandi.')
            return redirect('plan_detail', pk=plan.pk)
    else:
        form = PlanForm(instance=plan)
    
    context = {
        'form': form,
        'plan': plan,
        'title': f'"{plan.title}" rejasini tahrirlash',
    }
    return render(request, 'plans/plan_form.html', context)


@tutor_required
def plan_delete(request, pk):
    plan = get_object_or_404(Plan, pk=pk, tutor=request.user)
    
    if request.method == 'POST':
        plan_title = plan.title
        plan.delete()
        messages.success(request, f'Reja "{plan_title}" muvaffaqiyatli o\'chirildi.')
        return redirect('plan_list')
    
    context = {
        'plan': plan,
    }
    return render(request, 'plans/plan_confirm_delete.html', context)


@tutor_required
def add_reminder(request, plan_pk):
    plan = get_object_or_404(Plan, pk=plan_pk, tutor=request.user)
    
    if request.method == 'POST':
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.plan = plan
            reminder.save()
            messages.success(request, 'Eslatma muvaffaqiyatli qo\'shildi.')
            return redirect('plan_detail', pk=plan.pk)
    else:
        form = ReminderForm()
    
    context = {
        'form': form,
        'plan': plan,
        'title': f'"{plan.title}" uchun eslatma qo\'shish',
    }
    return render(request, 'plans/reminder_form.html', context)


@tutor_required
def update_plan_status(request, pk):
    plan = get_object_or_404(Plan, pk=pk, tutor=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Plan.STATUS_CHOICES):
            plan.status = new_status
            if new_status == 'completed':
                plan.completed_at = timezone.now()
            plan.save()
            messages.success(request, 'Reja holati yangilandi.')
    
    return redirect('plan_detail', pk=plan.pk)
