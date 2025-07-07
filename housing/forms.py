from django import forms
from .models import HousingInspection, InspectionPhoto


class HousingInspectionForm(forms.ModelForm):
    class Meta:
        model = HousingInspection
        fields = ['condition', 'comment']
        widgets = {
            'condition': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class InspectionPhotoForm(forms.ModelForm):
    class Meta:
        model = InspectionPhoto
        fields = ['photo', 'caption']
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
        }
from django import forms
from .models import Room
from students.models import  District

from django import forms
from .models import Room

from django import forms
from .models import Room

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'address', 'room_number', 'room_type', 'area', 'rent_price',
            'has_kitchen', 'has_bathroom', 'has_internet', 'has_heating',
            'condition', 'landlord_name', 'landlord_phone', 'notes',
            'latitude', 'longitude'  # Ensure these are included
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'room_number': forms.TextInput(),
            'room_type': forms.Select(),
            'area': forms.NumberInput(),
            'rent_price': forms.NumberInput(),
            'has_kitchen': forms.CheckboxInput(),
            'has_bathroom': forms.CheckboxInput(),
            'has_internet': forms.CheckboxInput(),
            'has_heating': forms.CheckboxInput(),
            'condition': forms.Select(),
            'landlord_name': forms.TextInput(),
            'landlord_phone': forms.TextInput(),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')

        # Validate latitude and longitude if provided
        if latitude is not None:
            if not -90 <= latitude <= 90:
                self.add_error('latitude', 'Kenglik -90 dan 90 gacha bo‘lishi kerak.')
        if longitude is not None:
            if not -180 <= longitude <= 180:
                self.add_error('longitude', 'Uzunlik -180 dan 180 gacha bo‘lishi kerak.')

        return cleaned_data