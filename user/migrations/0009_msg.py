# Generated by Django 4.2.2 on 2023-06-13 06:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_remove_usersignin_city_remove_usersignin_doorno_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='msg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(null=True)),
                ('userid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.usersignin')),
            ],
        ),
    ]