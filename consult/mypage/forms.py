from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

NATION = (('Korean', 'Korean'), ('English', 'English'), ('Japanese', 'Japanese'), 
          ('Chinese', 'Chinese'), ('Vietnamese', 'Vietnamese'), ('Thai', 'Thai'))

class CustomerChangeForm(UserChangeForm):
    image = forms.ImageField(label="image")
    email = forms.EmailField(label='Email Address')
    phone_number = forms.CharField(label='Phone Number', max_length=11)
    nation = forms.ChoiceField(label='Language', choices=NATION)
    class Meta:
        model = get_user_model()
        fields = ['image', 'email', 'phone_number', 'nation']
        
class CustomerImageChangeForm(UserChangeForm):
    image = forms.ImageField(label="image")
    class Meta:
        model = get_user_model()
        fields = ['image']
        
class CheckPasswordForm(forms.Form):
    password = forms.CharField(label='비밀번호', widget=forms.PasswordInput(
        attrs={'class': 'form-control',}), 
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = self.user.password
        
        if password:
            if not check_password(password, confirm_password):
                self.add_error('password', 'Passwords do not match.')
