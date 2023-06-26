from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

MEMBER_TYPE = (('Customer', 'Customer'), ('Counselor', 'Counselor'))
NATION = (('Korean', 'Korean'), ('English', 'English'), ('Japanese', 'Japanese'), 
          ('Chinese', 'Chinese'), ('Vietnamese', 'Vietnamese'), ('Thai', 'Thai'))

# Create your models here.
class User(AbstractUser):
    image = models.ImageField(upload_to="userImages/", null=True)
    phone_number = models.CharField(max_length=11)
    member_type = models.CharField(choices=MEMBER_TYPE, max_length=20)
    nation = models.CharField(choices=NATION, max_length=20)
    chat_active = models.BooleanField(default=False)
    voice_active = models.BooleanField(default=False)
    enter_voicechat = models.DateTimeField(null=True)
    enter_chat = models.DateTimeField(null=True)
    
    def __str__(self):
        return str(self.username)
    
