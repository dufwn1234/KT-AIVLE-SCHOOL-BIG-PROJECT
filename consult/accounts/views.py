from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from accounts.forms import LoginForm, SignUpForm
from django.core.mail.message import EmailMessage
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import resolve_url
from django.core.exceptions import ValidationError
from django.conf import settings
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views import generic, View
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
try:
    from django.utils import simplejson as json
except ImportError:
    import json
from django.views.decorators.http import require_POST
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
    logout as auth_logout, update_session_auth_hash,
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.decorators import method_decorator
# from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from chat.models import Chat
# from call.models import Call

User = get_user_model()
INTERNAL_RESET_URL_TOKEN = 'set-password'
INTERNAL_RESET_SESSION_TOKEN = '_password_reset_token'

def index(request):
    user = User.objects.get(username=request.user.username)
    user.chat_active = False
    user.save()
    return render(request, 'home.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
    
        if form.is_valid():
            user = form.save()
            return redirect('/')
        # else:
        #     messages.error(request, '회원가입에 실패했습니다.')
        #     print(form.errors)

        # 유효성 검사 실패, 에러가 있는 경우
        return render(request, 'signup_form.html', {'form': form})
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})

def signup_form(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # 유효성 검사 통과, 회원가입 성공
            user = form.save()
            return redirect('/')  # 회원가입 성공 후 이동할 URL

        # 유효성 검사 실패, 에러가 있는 경우
        return render(request, 'signup_form.html', {'form': form})

    # GET 요청인 경우 signup_form.html 템플릿 렌더링
    else:
        form = SignUpForm()
        
    return render(request, 'signup_form.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated: 
        return redirect('/') 
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                messages.warning(request, "로그인 정보가 올바르지 않습니다.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')

class UserPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    success_url = reverse_lazy('password_reset_done')
    form_class = PasswordResetForm
    
    def form_valid(self, form):
        if User.objects.filter(email=self.request.POST.get("email")).exists():
            return super().form_valid(form)
        else:
            return super().form_invalid(form)
            
class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'
    
class UserPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = SetPasswordForm
    success_url=reverse_lazy('password_reset_complete')
    template_name = 'password_reset_confirm.html'
    def form_valid(self, form):
        return super().form_valid(form)

class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_url'] = resolve_url(settings.LOGIN_URL)
        return context   

    