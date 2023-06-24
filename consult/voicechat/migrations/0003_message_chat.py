# Generated by Django 4.2 on 2023-06-24 11:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("voicechat", "0002_alter_message_user_chat"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="chat",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="voicechat_message_chat",
                to="voicechat.chat",
            ),
        ),
    ]
