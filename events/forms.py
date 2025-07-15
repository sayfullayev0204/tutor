from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Message, MessageReply
from faculty.models import Faculty

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['faculty', 'title', 'content', 'image']
        widgets = {
            'faculty': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Sarlavha kiriting')}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': _('Xabar matnini kiriting')}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'faculty': _('Fakultet'),
            'title': _('Sarlavha'),
            'content': _('Xabar matni'),
            'image': _('Rasm'),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_tutor():
            self.fields['faculty'].required = False
            self.fields['faculty'].widget.attrs['disabled'] = 'disabled'

class MessageReplyForm(forms.ModelForm):
    class Meta:
        model = MessageReply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': _('Javob matnini kiriting')}),
        }
        labels = {
            'content': _('Javob matni'),
        }