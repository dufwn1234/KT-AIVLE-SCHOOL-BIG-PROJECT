from django import forms
from .models import Chats

class ChatForm(forms.Form):
    title = forms.CharField(label='title')
    class Meta:
        model = Chats
        fields = ['title']