from django.shortcuts import render, redirect
from accounts.models import User
from chat.models import Chats
from call.models import Call
from django.contrib.auth.forms import UserChangeForm
from mypage.forms import CustomerChangeForm, CustomerImageChangeForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from mypage.forms import CheckPasswordForm
from django.contrib.auth import logout

# Create your views here.
@login_required
def mypage(request):
    form = CheckPasswordForm(request.user)
    img_form = CustomerImageChangeForm(instance=request.user)
    if request.user.member_type == 'Customer':
        chats = Chats.objects.filter(customer=request.user.id)
        calls = Call.objects.filter(customer=request.user.id)
    elif request.user.member_type == 'Counselor':
        chats = Chats.objects.filter(counselor=request.user.id)
        calls = Call.objects.filter(counselor=request.user.id)
        
    return render(request, 'mypage.html', {'chats':chats, 'calls':calls, 'img_form':img_form, 'form':form})

@login_required
def chatdetail(request, cpk):
    url = 'chatdetail' + '/' + cpk
    consult_type = 'chat'
    consult = Chats.objects.get(id=cpk)
        
    return render(request, 'mypage_detail.html', {'consult_type':consult_type, 'consult':consult, 'url':url})

@login_required
def calldetail(request, cpk):
    url = 'calldetail' + '/' + cpk
    consult_type = 'call'
    consult = Call.objects.get(id=cpk)
        
    return render(request, 'mypage_detail.html', {'consult_type':consult_type, 'consult':consult, 'url':url})

'''
@login_required
@require_http_methods(['GET', 'POST'])#mypage_update_test.html 만들어서 테스트중
def update(request):
    if request.method == 'POST':
        form = CustomerChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            if phone_number == '':
                phone_number = request.user.phone_number
            if email == '':
                email = request.user.email
            form.save()
            return redirect('mypage:mypage')
        else:
            return render(request, 'mypage_update_test.html', {'form':form})
    else:
        form = CustomerChangeForm(instance=request.user)
        return render(request, 'mypage_update_test.html', {'form':form})
'''
@login_required
@require_http_methods(['GET', 'POST'])
def update(request):
    if request.method == 'POST':
        form = CustomerChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            if phone_number == '':
                phone_number = request.user.phone_number
            if email == '':
                email = request.user.email
            form.save()
            return redirect('mypage:mypage')
        else:
            return render(request, 'mypage_update.html', {'form':form})
    else:
        form = CustomerChangeForm(instance=request.user)
        return render(request, 'mypage_update.html', {'form':form})
    
@login_required
@require_http_methods(['GET', 'POST'])
def img_update(request):
    if request.method == 'POST':
        img_form = CustomerImageChangeForm(request.POST, request.FILES, instance=request.user)
        if img_form.is_valid():
            img_form.save()
            return redirect('mypage:mypage')
        else:
            return render(request, 'mypage.html', {'img_form':img_form})
    else:
        img_form = CustomerImageChangeForm(instance=request.user)
        return render(request, 'mypage.html', {'img_form':img_form})
    
@login_required
@require_http_methods(['GET', 'POST'])
def img_delete(request):
    user = request.user
    user.image.delete()
    return redirect('mypage:mypage')

@login_required
def delete(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = CheckPasswordForm(request.user, request.POST)
            
            if form.is_valid():
                request.user.delete()
                logout(request)
                messages.success(request, "Membership withdrawal is complete.")
                return redirect('/')
        else:
            form = CheckPasswordForm(request.user)
        
    return render(request, 'mypage_delete.html', {'form':form})

def delete_account(request):
    pass

