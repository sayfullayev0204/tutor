from django import forms
from django.core.exceptions import ValidationError
from .models import Student, Region, District, TTJ
from housing.models import Room

class StudentForm(forms.ModelForm):
    ADD_NEW_ROOM = 'add_new'

    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'middle_name', 'gender', 'birth_date',
            'group', 'student_id', 'jshshir', 'passport', 'otm', 'talim_turi',
            'tulov_turi', 'talim_shakli', 'shifr', 'mutaxassislik', 'fuqaro',
            'country', 'const_region', 'const_district', 'address',
            'temporary_region', 'temporary_district', 'temporary_address',
            'appartment_type', 'room', 'ttj', 'family_type', 'phone_number',
            'email', 'is_orphan', 'has_disability', 'parent_status',
            'is_in_social_protection', 'is_in_temir_daftar', 'is_in_women_daftar',
            'is_in_youth_daftar', 'is_in_orphanage', 'parents_divorced',
            'bully_student'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'format': '%Y-%m-%d'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'temporary_address': forms.Textarea(attrs={'rows': 3}),
            'const_region': forms.Select(attrs={'id': 'id_const_region'}),
            'const_district': forms.Select(attrs={'id': 'id_const_district'}),
            'temporary_region': forms.Select(attrs={'id': 'id_temporary_region'}),
            'temporary_district': forms.Select(attrs={'id': 'id_temporary_district'}),
            'room': forms.Select(attrs={'id': 'id_room'}),
            'ttj': forms.Select(attrs={'id': 'id_ttj'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+998'}),
            'email': forms.EmailInput(attrs={'placeholder': 'example@domain.com'}),
            'jshshir': forms.TextInput(attrs={'maxlength': 14}),
            'passport': forms.TextInput(attrs={'maxlength': 20}),
            'shifr': forms.TextInput(attrs={'maxlength': 20}),
            'parent_status': forms.TextInput(attrs={'placeholder': 'Masalan: Otasi vafot etgan'}),
            'is_orphan': forms.CheckboxInput(),
            'has_disability': forms.CheckboxInput(),
            'is_in_social_protection': forms.CheckboxInput(),
            'is_in_temir_daftar': forms.CheckboxInput(),
            'is_in_women_daftar': forms.CheckboxInput(),
            'is_in_youth_daftar': forms.CheckboxInput(),
            'is_in_orphanage': forms.CheckboxInput(),
            'parents_divorced': forms.CheckboxInput(),
            'bully_student': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate room choices with "Add New Room" option
        self.fields['room'].queryset = Room.objects.all()
        self.fields['room'].choices = [
            (None, '---------'),
            (self.ADD_NEW_ROOM, 'Yangi xona qo‘shish')
        ] + [(room.id, str(room)) for room in Room.objects.all()]

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
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        jshshir = cleaned_data.get('jshshir')
        passport = cleaned_data.get('passport')

        # Clear ttj and room in cleaned_data based on appartment_type
        if appartment_type != 'ttj':
            cleaned_data['ttj'] = None
            cleaned_data['lives_in_dormitory'] = False
        else:
            cleaned_data['lives_in_dormitory'] = True

        if appartment_type != 'rent':
            cleaned_data['room'] = None
            cleaned_data['is_renting'] = False
        else:
            cleaned_data['is_renting'] = True

        # Validate appartment_type and related fields
        if appartment_type == 'rent' and not room:
            self.add_error('room', "Ijara xonadon tanlanganda 'xona' maydoni to'ldirilishi kerak.")
        elif appartment_type == 'ttj' and not ttj:
            self.add_error('ttj', "TTJ tanlanganda 'TTJ' maydoni to'ldirilishi kerak.")
        elif appartment_type == 'home' and (room or ttj):
            self.add_error(None, "'Uyda yashaydi' tanlanganda 'xona' yoki 'TTJ' maydonlari bo'sh bo'lishi kerak.")

        # Validate region-district consistency
        if const_region and const_district and const_district.region != const_region:
            self.add_error('const_district', "Doimiy tuman doimiy viloyatga mos kelmaydi.")
        if temporary_region and temporary_district and temporary_district.region != temporary_region:
            self.add_error('temporary_district', "Vaqtincha tuman vaqtincha viloyatga mos kelmaydi.")

        # Validate required fields
        if not first_name:
            self.add_error('first_name', "Ism maydoni to'ldirilishi kerak.")
        if not last_name:
            self.add_error('last_name', "Familiya maydoni to'ldirilishi kerak.")
        if not jshshir:
            self.add_error('jshshir', "JSHSHIR maydoni to'ldirilishi kerak.")
        elif len(jshshir) != 14:
            self.add_error('jshshir', "JSHSHIR 14 ta belgidan iborat bo'lishi kerak.")
        if not passport:
            self.add_error('passport', "Pasport maydoni to'ldirilishi kerak.")

        return cleaned_data

from django import forms

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel faylni yuklang',
        help_text='Faqat .xls yoki .xlsx formatidagi fayllar qabul qilinadi.',
        widget=forms.FileInput(attrs={'accept': '.xls,.xlsx'})
    )

    def clean_excel_file(self):
        excel_file = self.cleaned_data['excel_file']
        if not excel_file.name.lower().endswith(('.xls', '.xlsx')):
            raise forms.ValidationError("Faqat .xls yoki .xlsx formatidagi fayllar qabul qilinadi.")
        # Fayl hajmini cheklash (masalan, 10MB)
        if excel_file.size > 10 * 1024 * 1024:
            raise forms.ValidationError("Fayl hajmi 10MB dan oshmasligi kerak.")
        return excel_file