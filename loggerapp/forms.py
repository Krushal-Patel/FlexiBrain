from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordResetForm
from .models import PredictionLog
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings


class LogEntryForm(forms.ModelForm):
    class Meta:
        model = PredictionLog
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter your sentence here...'}),
        }


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Add a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        import re
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        if not re.search(r'\d', password):
            raise forms.ValidationError("Password must include at least one number.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError("Password must include at least one special character.")
        return password
    
class CustomPasswordResetForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150)
    email = forms.EmailField(label='Registered Email')

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if not User.objects.filter(username=username, email=email).exists():
            raise forms.ValidationError("No user found with this username and email combination.")
        
        return cleaned_data

    def save(self, request, **kwargs):
        user = User.objects.get(
            username=self.cleaned_data['username'],  # self.cleaned_data is a dictionary that Django forms use to store validated and cleaned input data from the user.
            email=self.cleaned_data['email'],
            is_active=True  # The user account is active
        )

        token = default_token_generator.make_token(user)  # token is a secure password-reset token.

        uid = urlsafe_base64_encode(force_bytes(user.pk))  # uid is a special ID for the user, encoded so it's safe in the URL.

        # Build password reset link
        reset_link = request.build_absolute_uri(f"/reset/{uid}/{token}/")

        subject = "🔐 Reset your FlexiBrain Password"
        message = render_to_string("password/password_reset_email.html", {
            'user': user,
            'reset_link': reset_link,
        })

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False, # If sending fails, raise an error
        )