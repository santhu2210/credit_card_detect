from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.utils.translation import gettext as _


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
        print("inside login form", username)
        
        password = forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control", "placeholder":"Password" }))

        #self.fields['username'].widget.attrs['placeholder'] = u'Email'
        #self.fields['password'].widget.attrs['placeholder'] = u'Password'

        # self.helper = FormHelper()
        # self.helper.layout = Layout(
        #     Div(
        #         'username', css_class='input-wrapper'
        #     ),
        #     Div(
        #         'password', css_class='input-wrapper'
        #     ),
        #     ButtonHolder(
        #         Submit('login', 'Login', css_class='btn-primary')
        #     )
        # )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                return self.cleaned_data
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data




class LoginNewForm(forms.Form):
   user = forms.CharField(widget=forms.TextInput(attrs={'class':'form-group form-control'}))
   password = forms.CharField(widget = forms.PasswordInput())


class DashboardForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','required': 'false'}))
    body = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control','required': 'false'}))
    file = forms.FileField()