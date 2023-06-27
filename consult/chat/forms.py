from django import forms
from .models import Chats

class ChatForm(forms.Form):
    summary = forms.CharField(label='summary')
    title = forms.CharField(label='title')
    class Meta:
        model = Chats
        fields = ['summary', 'title']