# Generated by Django 4.2.2 on 2023-06-13 09:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_remove_message_users_message_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='entrydate',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]