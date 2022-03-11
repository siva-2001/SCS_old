from django import forms
from .models import Competition, Player, VolleyballTeam, Match
from django.forms.widgets import DateTimeInput, TextInput, Textarea
#from crispy_forms.helper import FormHelper
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CreateCompetitionsForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ['name', 'discription', 'lastTimeForApplications', 'organizerName', 'theNumberOfTeamsRequiredToStartTheCompetition']
        widgets = {
            'theNumberOfTeamsRequiredToStartTheCompetition':TextInput(attrs={
                'id': 'id_datetimepicker',
                'type': "text",
                'class': "form-control",
                'placeholder': "Минимальное количество команд, необходимое для начала соревнований",
                'required': ''
            }),
            'lastTimeForApplications':DateTimeInput(attrs={
                'id':'id_datetimepicker',
                'type':"text",
                'class':"form-control",
                'placeholder':"Время подачи заявок на участие",
                'required':''
            }),
            'name':TextInput(attrs={
                'id': 'id_name',
                'type': "text",
                'class': "form-control",
                'placeholder': "Заголовок",
                'required': ''
            }),
            'discription':Textarea(attrs={
                'id': 'id_discription',
                'type': "text",
                'class': "form-control",
                'placeholder': "Описание предстоящих соревнований",
                'required': '',
                'style':'resize:none;'
            }),
            'organizerName': TextInput(attrs={
                'id': 'id_organizerName',
                'type': "text",
                'class': "form-control",
                'placeholder': "Наименование организации, проводящей соревнования",
                'required': ''
            })
        }
        labels = {
            'lastTimeForApplications':'Заявки подаются до:',
            'name':'Заголовок:',
            'discription':'Описание:',
            'organizerName':'Организатор',
        }

class RegistrPlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'surename', 'patronymic', 'age']
        widgets = {
            'name':TextInput(attrs={
                'class': "form-control",
                'placeholder': "Имя",
                'required': ''
            }),
            'surename': TextInput(attrs={
                'class': "form-control",
                'placeholder': "Фамилия",
                'required': ''
            }),
            'patronymic': TextInput(attrs={
                'class': "form-control",
                'placeholder': "Отчество",
            }),
            'age': TextInput(attrs={
                'class': "form-control",
                'placeholder': "Возраст",
                'required': ''
            })
        }

class RegistrVolleybolTeamForm(forms.ModelForm):
    class Meta:
        model = VolleyballTeam
        fields = ['name', 'discription']
        labels = {
            'name':"Название команды",
            "discription":'Описание',

        }
        widgets = {
            'name': TextInput(attrs={
                'id': 'id_teamName',
                'type': "text",
                'class': "form-control",
                'placeholder': "Название команды",
                'required': ''
            }),
            'discription': Textarea(attrs={
                'id': 'id_teamDiscription',
                'type': "text",
                'class': "form-control",
                'placeholder': "Описание команды",
                'required': '',
                'style':'resize:none;'
            }),
        }

class MatchEditForm(forms.ModelForm):
    id = forms.IntegerField()
    class Meta:
        model = Match
        fields = ['name', 'place', 'matchDateTime', 'firstTeamScore', 'secondTeamScore']
        widgets = {
            'name':TextInput(attrs={
                'id': 'id_name',
                'type': "text",
                'class': "form-control",
                'placeholder': "Заголовок",
                'required': ''
            }),
            'place':TextInput(attrs={
                'id': 'id_place',
                'type': "text",
                'class': "form-control",
                'placeholder': "Название или адрес спорткомплекса",
                'required': '',
            }),
            'matchDateTime':DateTimeInput(attrs={
                'id':'id_datetimepicker',
                'type':"text",
                'class':"form-control",
                'placeholder':"Время проведения матча",
                'required':'',
            }),
            'firstTeamScore': TextInput(attrs={
                'id': 'id_place',
                'type': "text",
                'class': "form-control scoreEditor",
                'placeholder': "Название или адрес спорткомплекса",
                'required': '',
            }),
            'secondTeamScore': TextInput(attrs={
                'id': 'id_place',
                'type': "text",
                'class': "form-control scoreEditor",
                'placeholder': "Название или адрес спорткомплекса",
                'required': '',
            }),

        }

class SignUpUser(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': 'Логин:',
            'email':'E-mail:',
            'first_name': 'Имя',
            'last_name': 'Фамилия'
        }


