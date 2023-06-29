from django.contrib import admin
from .models import Chat, Contact, Message, Chats

# Register your models here.
admin.site.register(Chat)
admin.site.register(Contact)
admin.site.register(Message)
admin.site.register(Chats)