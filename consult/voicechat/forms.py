from django import forms
from call.models import Call

class VoiceChatForm(forms.Form):
    summary = forms.CharField(label='summary')
    title = forms.CharField(label='title')
    class Meta:
        model = Call
        fields = ['summary', 'title']
        