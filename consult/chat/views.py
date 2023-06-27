from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from . import models
from accounts.models import User
from .models import Chat, Contact, Message
from call.models import Call
from boards.models import Post
from django.utils.safestring import mark_safe
from datetime import datetime
from .forms import ChatForm
from .models import Chats


import openai #추가(0619)
from django.http import JsonResponse#추가(0619)
from django.http import HttpResponse
import json
import bardapi
import os


# Create your views here.
openai.api_key = "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" #추가(0619) 프로젝트 끝나고 API키 삭제 예정

#######(0619테스트용)####################
def translater(request):
    data = json.loads(request.body)
    language = data["language"]
    text = data["text"]

    prompt = f"{text}\n\nTranslate this sentence into {language}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "you are a translater"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=500,
    )
    
    result=response["choices"][0]["message"]["content"]
    if "Note:" in result:
        result=result.split("Note:",1)[0].strip()
    #return JsonResponse({"result":result},json_dumps_params={'ensure_ascii': False})
    return HttpResponse(result, content_type="text/plain; charset=utf-8")
    #return JsonResponse({"result":response["choices"][0]["message"]["content"]},json_dumps_params={'ensure_ascii': False})

def test2(request):
    return render(request, 'chat/test2.html')


@login_required
def test1(request):
    if request.user.is_authenticated:
        # 채팅방 목록
        chat_rooms = Contact.objects.filter(user=request.user)
        print(chat_rooms)
        
        return render(request, 'chat/test1.html')
    else:
        return redirect('accounts:login')

def translater1(request):
    data = json.loads(request.body)
    language1 = data["language1"]
    language2 = data["language2"]
    text = data["text"]
    
    prompt = f"{text}\n\nTranslate this sentence from {language1} to {language2}"
    response = openai.ChatCompletion.create(
         model="gpt-3.5-turbo",
        messages=[
                {
                    "role": "system",
                    "content": "you are a translater"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=500,
        )

    result = response["choices"][0]["message"]["content"]
    if "Note:" in result:
            result = result.split("Note:", 1)[0].strip()

    return HttpResponse(result, content_type="text/plain; charset=utf-8")

def translater2(request):
    data = json.loads(request.body)
    language1 = data["language1"]
    #language2 = data["language2"]
    text = data["text"]
    
    prompt = f"{text}\n\nTranslate this sentence into {language1}"
    #prompt = f"{text}\n\nTranslate this sentence from {language1} to {language2}"
    response = openai.ChatCompletion.create(
         model="gpt-3.5-turbo",
        messages=[
                {
                    "role": "system",
                    "content": "you are a translater"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=500,
        )

    result = response["choices"][0]["message"]["content"]
    if "Note:" in result:
            result = result.split("Note:", 1)[0].strip()

    return HttpResponse(result, content_type="text/plain; charset=utf-8")    
################################################################33
###### 코드 정리 하면서 진행 부탁 드립니다 #######

@login_required
def chat(request):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        user.chat_active = False
        user.save()
        
        # 채팅방 목록
        counselor_list = User.objects.filter(member_type='Counselor')
        context = {
            'counselor_list': counselor_list
        }
        
        return render(request, 'chat/chat.html', context)
    else:
        return redirect('accounts:login')

@login_required
def room(request, room_name):
    # chat_active 변경
    user = User.objects.get(username=request.user.username)
    user.chat_active = True
    if user.member_type == 'Counselor':  # 상담사일 경우, 입장 시간 저장되도록
        user.enter_chat = datetime.now()
    user.save()
    
    # 상담사 정보
    counselor = User.objects.get(id=room_name)
    
    # 고객 정보  --> 수정 중
    customer = None
    if request.user.member_type == 'Customer':
        customer = User.objects.get(id=request.user.id)
    
    # message = Message.objects.latest('timestamp')
    # customer = User.objects.get(id=message.user_id)
        
    customers = User.objects.filter(member_type='Customer')
    chats = Chats.objects.all()
    calls = Call.objects.all()
    
    # FAQ
    faqs = Post.objects.filter(category='FAQ')
        
    return render(request, "chat/room_.html", {"room_name": mark_safe(json.dumps(room_name)),
                                                'username': request.user.username,
                                                'counselor':counselor, 'customer':customer, 
                                                'customers':customers, 'chats':chats, 'calls':calls,
                                                'faqs':faqs})
    
@login_required
def chat_end(request):
    # 고객 정보
    room_messages = Message.objects.filter(room_name=request.user.id).order_by('timestamp')
    for m in room_messages:
        if m.user_id != request.user.id:
            customer = User.objects.get(id=m.user_id)
    
    # 상담 메시지 내용
    # __gte : 크거나 같다 __gt : 크다 __lt : 작다 __lte : 작거나 같다
    messages = Message.objects.filter(timestamp__gte=request.user.enter_chat, timestamp__lte=datetime.now(), room_name=request.user.id)
    
    # 전체 내용 
    all_contents = ''
    for m in messages:
        all_contents += m.content + '\n'
    print(all_contents)

    #  # 상담사 답변만
    # counselor_messages = Message.objects.filter(timestamp__gte=request.user.enter_chat, timestamp__lte=datetime.now(), 
    #                                             room_name=request.user.id, user_id=request.user.id)
    # counselor_contents = ''
    # for m in counselor_messages:
    #     counselor_contents += m.content + '\n'

    # # 요약 
    # os.environ["_BARD_API_KEY"] = "YAiTWs7-AlPSVY-_yC9KPsEbkpjroNJsDyZ_0fNuIsY5F-6fay2GKzTXsHIFKOvqyg3Okg."
    # input_text = all_contents + "\n Tl;dr"
    # response = bardapi.core.Bard().get_answer(input_text)

    # summary = response["choices"][0]["content"][0]  # 요약된 내용
    # print(summary)

    # chats에 저장
    if request.method == 'POST':
        form = ChatForm(request.POST)
        for field in form:
            if field.errors:
                print("Field Error:", field.name, field.errors)
        if form.is_valid():
            chat = Chats()
            chat.customer = customer
            chat.counselor = request.user
            chat.consult_text = all_contents
            chat.consult_date = datetime.now()
            # chat.summary = form.cleaned_data['summary']
            chat.title = form.cleaned_data['title']
            chat.save()
            return redirect('chat:chat')
        else:
            form = ChatForm()
        return render(request, 'chat/chat_end.html', {'form':form,'customer':customer, 'all_contents':all_contents})
        
    else:
        form = ChatForm()
        return render(request, 'chat/chat_end.html', {'form':form,'customer':customer, 'all_contents':all_contents}) 

def save_customer_info(chat_id, user):
    customer_info = User.objects.get(id=user.id)
    
def get_customer_info():
    return customer_info

def get_last_10_messages(chatId):
    chat = get_object_or_404(Chat, id=chatId)
    return chat.messages.order_by('-timestamp').all()[:10]

def get_user_contact(username):
    user = get_object_or_404(User, username=username)
    return get_object_or_404(Contact, user=user)

def get_current_chat(chatId):
    return get_object_or_404(Chat, id=chatId)
