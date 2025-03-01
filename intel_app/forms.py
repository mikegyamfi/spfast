from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from . import models


class CustomUserForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control phone-num'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'password1', 'password2']


class IShareBundleForm(forms.Form):
    phone_number = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control phone', 'placeholder': '0270000000'}))
    offers = forms.ModelChoiceField(queryset=models.IshareBundlePrice.objects.all().order_by('price'), to_field_name='price', empty_label=None,
                                    widget=forms.Select(attrs={'class': 'form-control airtime-input'}))


    def __init__(self, status, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if status == "User":
            self.fields['offers'].queryset = models.IshareBundlePrice.objects.all()
        elif status == "Agent":
            self.fields['offers'].queryset = models.AgentIshareBundlePrice.objects.all()
        # self.fields['size'].queryset = models.Size.objects.filter(domain=domain)

            

class MTNForm(forms.Form):
    phone_number = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control mtn-phone', 'placeholder': '0200000000'}))
    offers = forms.ModelChoiceField(queryset=models.MTNBundlePrice.objects.all().order_by('price'), to_field_name='price', empty_label=None,
                               widget=forms.Select(attrs={'class': 'form-control mtn-offer'}))


    def __init__(self, status, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if status == "User":
            self.fields['offers'].queryset = models.MTNBundlePrice.objects.all().order_by('price')
        elif status == "Agent":
            self.fields['offers'].queryset = models.AgentMTNBundlePrice.objects.all().order_by('price')
        # self.fields['size'].queryset = models.Size.objects.filter(domain=domain)



class CreditUserForm(forms.Form):
    user = forms.ModelChoiceField(queryset=models.CustomUser.objects.all().order_by('username'), to_field_name='username', empty_label=None,
                                  widget=forms.Select(attrs={'class': 'form-control airtime-input'}))
    amount = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'GHS 100'}))


class UploadFileForm(forms.Form):
    file = forms.FileField(label='Select an Excel file', help_text='Allowed file formats: .xlsx')


