# Generated by Django 5.0.7 on 2024-08-05 11:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_remove_student_attendence_attendence_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.student'),
        ),
    ]
