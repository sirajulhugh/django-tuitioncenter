# Generated by Django 5.0.7 on 2024-08-10 07:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_student_binary_data_teacher_binary_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='course',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='app.course'),
        ),
    ]
