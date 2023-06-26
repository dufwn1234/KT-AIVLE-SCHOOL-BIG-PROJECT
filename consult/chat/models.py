from django.db import models
from accounts.models import User

# Create your models here.
class Message(models.Model):
    user = models.ForeignKey('accounts.User', related_name='message_user', on_delete=models.CASCADE)
    chat = models.ForeignKey('Chat', related_name='message_chat', on_delete=models.CASCADE, null=True)
    room_name = models.ForeignKey('accounts.User', related_name='chat_room_name', on_delete=models.CASCADE, null=True) 
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
class Chat(models.Model):
    id = models.BigAutoField(primary_key=True)
    
    user = models.ForeignKey('accounts.User', related_name='chat_user', on_delete=models.CASCADE)
    contact = models.ForeignKey('Contact', related_name='chat_contact', on_delete=models.CASCADE, null=True)
    message = models.ForeignKey('Message', related_name='chat_messages', on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    
    @classmethod
    def last_10_messages(self):
        return Chat.objects.order_by('-timestamp').all()[:10]
    
    # def last_10_messages(self, caht_id):
    #     return Message.objects.filter(chat_id=chat_id).order_by('created_at')[:10]
    
class Contact(models.Model):
    user = models.ForeignKey('accounts.User', related_name='contact_user', on_delete=models.CASCADE)
    chat = models.ForeignKey('Chat', related_name='contact_chat', on_delete=models.CASCADE)
    

class Chats(models.Model):
    id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey('accounts.User', related_name='chat_customer', on_delete=models.CASCADE)
    counselor = models.ForeignKey('accounts.User', related_name='chat_counselor', on_delete=models.CASCADE)
    consult_text = models.TextField()
    consult_date = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(null=True)
    title = models.TextField()
