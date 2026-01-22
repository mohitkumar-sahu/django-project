from django import forms
from django.contrib.auth.models import User
from learnapp.models import UserDetails
from django_recaptcha.fields import ReCaptchaField

class UserForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model=User
        # fields='__all__'
        fields=['username','email','password']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model=UserDetails
        fields=['phone','address','street','city','zipcode','userpic']
    captcha = ReCaptchaField()

class userUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email']

class userProfileUpdate(forms.ModelForm):
    class Meta:
        model=UserDetails
        fields=['phone','address','street','city','zipcode','userpic']
