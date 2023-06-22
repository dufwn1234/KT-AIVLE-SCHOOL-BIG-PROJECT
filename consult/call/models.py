from django.db import models
from accounts.models import User

SATICFACTION = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'))

# Create your models here.
class Call(models.Model):
    id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey('accounts.User', related_name='call_customer', on_delete=models.CASCADE)
    counselor = models.ForeignKey('accounts.User', related_name='call_counselor', on_delete=models.CASCADE)
    consult_audio = models.TextField()
    consult_text = models.TextField()
    consult_date = models.DateTimeField(auto_now_add=True)
    summary = models.TextField()
    title = models.TextField(null=True)
    satisfaction = models.CharField(choices=SATICFACTION, max_length=1)