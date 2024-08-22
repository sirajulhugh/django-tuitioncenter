from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    name = models.CharField(max_length=100)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    syllabus=models.FileField(upload_to='image/',null=True, blank=True)
    duration = models.IntegerField()

class Task(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='image/',null=True, blank=True)
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey('Student', on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE,  null=True, blank=True)

class Attendence(models.Model):
    date = models.DateField()
    status = models.CharField(max_length=10)
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey('Student', on_delete=models.CASCADE, null=True, blank=True)

class Student(models.Model):
    age = models.IntegerField()
    address = models.TextField()
    date_of_join = models.DateField()
    images=models.ImageField(upload_to='image/',null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    binary_data = models.BinaryField(default=False)

class Teacher(models.Model):
    age=models.IntegerField(null=True)
    phnoenumber=models.CharField(max_length=10)
    address=models.CharField(max_length=20)    
    images=models.ImageField(upload_to='image/',null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE,null=True, blank=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    binary_data = models.BinaryField(default=False)

    

