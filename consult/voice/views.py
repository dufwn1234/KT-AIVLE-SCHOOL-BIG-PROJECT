from django.shortcuts import render,redirect,HttpResponse
from accounts.models import User
from django.utils import timezone
from .models import Voice




def test(request):
    username = None
    counselor_list = User.objects.filter(member_type='Counselor')
    if request.user.is_authenticated:  # 사용자가 인증된 경우에만 사용자 이름 가져오기
        username = request.user.username
    #     counselor_list = User.objects.all()
    
    context = {
        'username': username,
        'counselor_list': counselor_list
    }
    
    if request.method == 'POST':
        action = request.POST.get('action')
        counselor_username = request.POST.get('counselor')
        
        if action == 'start':
            # 전화 시작 시간을 저장
            request.session['start_time'] = timezone.now()
        elif action == 'stop':
            # 전화 종료 시간을 저장
            start_time = request.session.pop('start_time', None)
            
            if start_time:
                end_time = timezone.now()
                duration = (end_time - start_time).total_seconds() / 60
                
                # 시작 시간과 종료 시간을 DB에 저장
                call = Voice(caller=username, receiver=counselor_username, start_time=start_time, end_time=end_time, duration=duration)
                call.save()

    return render(request, 'voice.html', context)


def test1(request):
    username = None
    counselor_list = User.objects.filter(member_type='Counselor')
    if request.user.is_authenticated:  # 사용자가 인증된 경우에만 사용자 이름 가져오기
        username = request.user.username
    #     counselor_list = User.objects.all()
    
    context = {
        'username': username,
        'counselor_list': counselor_list
    }
    return render(request, 'voice_test.html', context)

def counselor(request):
    username = None
    counselor_list = User.objects.filter(member_type='Counselor')
    if request.user.is_authenticated:  # 사용자가 인증된 경우에만 사용자 이름 가져오기
        username = request.user.username
    #     counselor_list = User.objects.all()
    
    context = {
        'username': username,
        'counselor_list': counselor_list
    }
    return render(request, 'voice_counselor.html', context)

def client(request):
    username = None
    counselor_list = User.objects.filter(member_type='Counselor')
    if request.user.is_authenticated:  # 사용자가 인증된 경우에만 사용자 이름 가져오기
        username = request.user.username
    #     counselor_list = User.objects.all()
    
    context = {
        'username': username,
        'counselor_list': counselor_list
    }
    return render(request, 'voice_client.html', context)

def voice_en(request):
    return render(request, 'voice_en.html')

def voice_ja(request):
    return render(request, 'voice_ja.html')

def voice_ch(request):
    return render(request, 'voice_ch.html')

def voice_vi(request):
    return render(request, 'voice_vi.html')

def voice_th(request):
    return render(request, 'voice_th.html')

def account(request):
    return render(request, 'account.html')

def summary(request):
    return render(request, 'summary.html')

def history(request):
    return render(request, 'history.html')

