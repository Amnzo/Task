from django import forms
from .models import Task, Door
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Nom d\'utilisateur',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre nom d\'utilisateur'
        })
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre mot de passe'
        })
    )

class DoorCreationForm(UserCreationForm):
    class Meta:
        model = Door
        fields = ['email', 'password1', 'password2', 'niveau']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'niveau': forms.Select(attrs={'class': 'form-select'})
        }

from .models import Task, Door, STATUS_CHOICES, IMPORTANCE_CHOICES

class TaskForm(forms.ModelForm):
    assigne_a = forms.ModelChoiceField(
        queryset=Door.objects.all(),
        widget=forms.HiddenInput(),
        required=False
    )
    importance = forms.ChoiceField(
        choices=IMPORTANCE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='MEDIUM',
        required=True
    )

    class Meta:
        model = Task
        fields = ['description', 'importance', 'assigne_a']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter task description'}),
            'assigne_a': forms.HiddenInput()
        }

class TaskAdminForm(forms.ModelForm):
    importance = forms.ChoiceField(
        choices=IMPORTANCE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='MEDIUM',
        required=True
    )

    class Meta:
        model = Task
        fields = ['description', 'status', 'importance', 'assigne_a']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter task description'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigne_a': forms.Select(attrs={'class': 'form-select'})
        }
