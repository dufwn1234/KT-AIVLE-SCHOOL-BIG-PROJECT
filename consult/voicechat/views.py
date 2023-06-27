from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import User
from .models import Chat, Contact, Message
from call.models import Call
from chat.models import Chats
from boards.models import Post
from django.utils.safestring import mark_safe
import json
from datetime import datetime
from .forms import VoiceChatForm
from django.conf import settings
import bardapi
import os
from twilio.rest import Client
from datetime import date
# Create your views here.

@login_required
def voicechat(request):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        user.voice_active = False
        user.save()
        
        counselor_list = User.objects.filter(member_type='Counselor')
        context = {
            'counselor_list': counselor_list
        }
        
        return render(request, 'voicechat.html', context)
    else:
        return redirect('accounts:login')
    
    
def calldraft(request):
    return render(request, 'call_draft.html')

    
    
@login_required
def room(request, room_name):
    user = User.objects.get(username=request.user.username)
    user.voice_active = True
    if user.member_type == 'Counselor':  # 상담사일 경우, 입장 시간 저장되도록
        user.enter_voicechat = datetime.now()
    user.save()
    
    # 상담사 정보
    counselor = User.objects.get(id=room_name)
    
    # 고객 정보  --> 수정 중
    customer = None
    if request.user.member_type == 'Customer':
        customer = User.objects.get(id=request.user.id)
        
    customers = User.objects.filter(member_type='Customer')
    chats = Chats.objects.all()
    calls = Call.objects.all()
    
    # FAQ
    faqs = Post.objects.filter(category='FAQ')
    
    # api key, region
    key = settings.TTS_API_KEY
    region = settings.TTS_REGION
        
    return render(request, "room_.html", {"room_name": mark_safe(json.dumps(room_name)),
                                                'username': request.user.username,
                                                'counselor':counselor, 'customer':customer, 
                                                'customers':customers, 'chats':chats, 'calls':calls,
                                                'faqs':faqs, 'key':key, 'region':region})

@login_required
def voicechat_end(request):
    # 고객 정보
    room_messages = Message.objects.filter(room_name=request.user.id).order_by('timestamp')
    for m in room_messages:
        if m.user_id != request.user.id:
            customer = User.objects.get(id=m.user_id)
    
    # 상담 메시지 내용
    # __gte : 크거나 같다 __gt : 크다 __lt : 작다 __lte : 작거나 같다
    messages = Message.objects.filter(timestamp__gte=request.user.enter_voicechat, timestamp__lte=datetime.now(), room_name=request.user.id)
    
    # 전체 내용 
    all_contents = ''
    for m in messages:
        all_contents += m.content + '\n'
    print(all_contents)
        
    # 상담사 답변만
    counselor_messages = Message.objects.filter(timestamp__gte=request.user.enter_voicechat, timestamp__lte=datetime.now(), 
                                                room_name=request.user.id, user_id=request.user.id)
    counselor_contents = ''
    for m in counselor_messages:
        counselor_contents += m.content + '\n'
    print(counselor_contents)
    
    # 요약 
    if counselor_contents == '':
        summary = ''
    else:
        os.environ["_BARD_API_KEY"] = "YAiTWs7-AlPSVY-_yC9KPsEbkpjroNJsDyZ_0fNuIsY5F-6fay2GKzTXsHIFKOvqyg3Okg."
        input_text = counselor_contents + "\n Tl;dr"
        response = bardapi.core.Bard().get_answer(input_text)

        summary = response["choices"][0]["content"][0]  # 요약된 내용
        # twilio(summary)
        print(summary)

    # call에 저장
    if request.method == 'POST':
        form = VoiceChatForm(request.POST)
        for field in form:
            if field.errors:
                print("Field Error:", field.name, field.errors)
        if form.is_valid():
            call = Call()
            call.customer = customer
            call.counselor = request.user
            call.consult_text = all_contents
            call.consult_date = datetime.now()
            call.summary = form.cleaned_data['summary']
            call.title = form.cleaned_data['title']
            call.save()
            return redirect('voicetalk:voicechat')
        else:
            form = VoiceChatForm()
        return render(request, 'voicechat_end.html', {'form':form,'customer':customer, 
                                                    'all_contents':all_contents, 'summary':summary})
        
    else:
        form = VoiceChatForm()
        return render(request, 'voicechat_end.html', {'form':form,'customer':customer, 
                                                    'all_contents':all_contents, 'summary':summary})
        
        
        



def sum(request):
    return render(request, 'sum.html')

def Bardd(prompt):
    os.environ["_BARD_API_KEY"] = "XQgOVGsSD7eGDvKozvshtguxw_ocrPgdqwOopYUDYMfX9B1FlsXc2bJ27Ip945izhZoYAA."
    input_text = prompt + " \n Tl;dr"
    response = bardapi.core.Bard().get_answer(input_text)
    # twilio(response["choices"][0]["content"][0])
    return response["choices"][0]["content"][0]
    
def my_view():
    today = date.today()
    formatted_date = today.strftime("%Y-%m-%d")
    return formatted_date
    
def summ(request):
    prompt = request.POST.get('question')
    result = Bardd(prompt)

    context = {
        'question': prompt,
        'result': result
    }

    return render(request, 'result.html', context) 


def twilio(prompt):
    account_sid = "ACa0a888268f1ccccc271e417826c74886"
    auth_token = "18d1c29db7eec5b093ee24bd6069e2f7"
    client = Client(account_sid, auth_token)
    a = my_view()
    message = client.messages.create(
    body ="\n" + a +"에 AI가 요약한 상담 내용입니다. \n" + prompt,
    from_="+13613154870",
    to="+821020631392"
    )