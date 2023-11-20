from django import forms
from django.forms import DateInput

from core.models import Group, GroupStudent, Course, Dars, Interested


class DatePicker(DateInput):
    template_name = "widgets/datepicker.html"


class GrStForm(forms.ModelForm):
    start_date = forms.DateField(
        required=True,
        label="O\'uqvchi qachondan qo\'shildi",
        widget=DatePicker,
    )

    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group')
        super().__init__(*args, **kwargs)
        self.fields['group'].initial = group

    class Meta:
        model = GroupStudent
        fields = '__all__'
        labels = {
            "group": "Guruhni tanlang",
            "student": 'O\'quvchini tanlang',
            "start_date": 'O\'uqvchi qachondan qo\'shildi',
        }

    def save(self, commit=True):
        instance = super(GrStForm, self).save(commit=commit)
        return instance


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'course', 'duration', 'status']


class DarsForm(forms.ModelForm):
    class Meta:
        model = Dars
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group')
        super().__init__(*args, **kwargs)
        self.fields['group'].initial = group


class InterestedForm(forms.ModelForm):
    class Meta:
        model = Interested
        fields = "__all__"


class EnrollForm(forms.ModelForm):
    class Meta:
        model = Interested
        # fields = '__all__'
        exclude = ['view', 'contacted']
        labels = {
            "name": "To'lliq ism Familiyangiz",
            "phone": "Telefon raqam",
            "telegram": "Telegram username",
            "extra_contact": "Qo'shimcha bog'lanish uchun manba",
            'additional': "Qiziqishingiz haqida qisqacha"
        }
