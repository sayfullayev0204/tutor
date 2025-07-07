from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .forms import ProfileForm


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        return '/dashboard/'


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil muvaffaqiyatli yangilandi!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/profile.html', context)


def logout_view(request):
    logout(request)
    messages.info(request, 'Siz tizimdan muvaffaqiyatli chiqdingiz.')
    return redirect('login')
