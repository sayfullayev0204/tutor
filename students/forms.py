from django import forms
from django.core.exceptions import ValidationError
from .models import Student, Region, District, TTJ
from housing.models import Room

class StudentForm(forms.ModelForm):
    ADD_NEW_ROOM = 'add_new'

    class Meta:
        model = Student
        fields = '__all__'
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'format': '%Y-%m-%d'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'temporary_address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'const_region': forms.Select(attrs={'id': 'id_const_region'}),
            'const_district': forms.Select(attrs={'id': 'id_const_district'}),
            'temporary_region': forms.Select(attrs={'id': 'id_temporary_region'}),
            'temporary_district': forms.Select(attrs={'id': 'id_temporary_district'}),
            'room': forms.Select(attrs={'id': 'id_room'}),
            'ttj': forms.Select(attrs={'id': 'id_ttj'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate room choices with "Add New Room" option
        self.fields['room'].queryset = Room.objects.all()
        self.fields['room'].choices = [(None, '---------')] + [(self.ADD_NEW_ROOM, 'Yangi xona qo‘shish')] + [(room.id, str(room)) for room in Room.objects.all()]
        
        # Initialize district fields
        self.fields['const_district'].queryset = District.objects.all()
        self.fields['temporary_district'].queryset = District.objects.all()
        
        # Filter districts based on instance or submitted data
        if self.instance and self.instance.pk:
            if self.instance.const_region:
                self.fields['const_district'].queryset = District.objects.filter(region=self.instance.const_region)
            if self.instance.temporary_region:
                self.fields['temporary_district'].queryset = District.objects.filter(region=self.instance.temporary_region)
        elif self.data:
            if 'const_region' in self.data:
                try:
                    const_region_id = int(self.data.get('const_region'))
                    self.fields['const_district'].queryset = District.objects.filter(region_id=const_region_id)
                except (ValueError, TypeError):
                    pass
            if 'temporary_region' in self.data:
                try:
                    temp_region_id = int(self.data.get('temporary_region'))
                    self.fields['temporary_district'].queryset = District.objects.filter(region_id=temp_region_id)
                except (ValueError, TypeError):
                    pass

        # Clear ttj and room based on appartment_type
        if 'appartment_type' in self.data:
            appartment_type = self.data.get('appartment_type')
            if appartment_type != 'ttj':
                self.fields['ttj'].initial = None
            if appartment_type != 'rent':
                self.fields['room'].initial = None
        elif self.instance.pk and hasattr(self.instance, 'appartment_type'):
            if self.instance.appartment_type != 'ttj':
                self.fields['ttj'].initial = None
            if self.instance.appartment_type != 'rent':
                self.fields['room'].initial = None

    def clean(self):
        cleaned_data = super().clean()
        appartment_type = cleaned_data.get('appartment_type')
        room = cleaned_data.get('room')
        ttj = cleaned_data.get('ttj')
        const_region = cleaned_data.get('const_region')
        const_district = cleaned_data.get('const_district')
        temporary_region = cleaned_data.get('temporary_region')
        temporary_district = cleaned_data.get('temporary_district')

        # Clear ttj and room in cleaned_data based on appartment_type
        if appartment_type != 'ttj':
            cleaned_data['ttj'] = None
        if appartment_type != 'rent':
            cleaned_data['room'] = None

        # Set is_renting and lives_in_dormitory based on appartment_type
        cleaned_data['is_renting'] = appartment_type == 'rent'
        cleaned_data['lives_in_dormitory'] = appartment_type == 'ttj'

        # Validate appartment_type and related fields
        if appartment_type == 'rent' and not room:
            self.add_error('room', "Ijara xonadon tanlanganda 'room' maydoni to'ldirilishi kerak.")
        elif appartment_type == 'ttj' and not ttj:
            self.add_error('ttj', "TTJ tanlanganda 'ttj' maydoni to'ldirilishi kerak.")
        elif appartment_type == 'home' and (room or ttj):
            self.add_error(None, "'Uyda yashaydi' tanlanganda 'room' yoki 'ttj' maydonlari bo'sh bo'lishi kerak.")
        
        # Validate region-district consistency
        if const_region and const_district and const_district.region != const_region:
            self.add_error('const_district', "Tuman doimiy viloyatga mos kelmaydi.")
        if temporary_region and temporary_district and temporary_district.region != temporary_region:
            self.add_error('temporary_district', "Tuman vaqtincha viloyatga mos kelmaydi.")

        return cleaned_data