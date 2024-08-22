# views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User,auth
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import Student, Teacher, Course, Task, Attendence
from django.contrib import messages
from django.contrib.auth import login,authenticate
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseForbidden
from datetime import datetime
import re
import random
import string
from django.contrib.auth.decorators import login_required

def register(request):
    return render(request, 'register.html')

def generate_random_digits(length):
    return ''.join(random.choices(string.digits, k=length))

def register_(request):
    error_message = None

    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        age = request.POST.get('age')
        address = request.POST.get('address')
        date_of_join = request.POST.get('date_of_join')
        phonenumber = request.POST.get('phonenumber')
        images = request.FILES.get('images')
        
        # Validation checks
        if User.objects.filter(username=username).exists():
            error_message = 'Username already exists. Please choose a different username.'
        elif User.objects.filter(email=email).exists():
            error_message = 'Email already exists. Please use a different email.'
        elif len(phonenumber) != 10 and user_type == 'teacher':
            error_message = 'Phone number must be 10 digits long.'
        elif user_type not in ['student', 'teacher']:
            error_message = 'Invalid user type selected.'

        if error_message:
            return render(request, 'register.html', {'error_message': error_message})

        # If no errors, proceed with user creation
        password = generate_random_digits(6)
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            is_staff=(user_type == 'teacher')
        )

        if user_type == 'student':
            Student.objects.create(
                user=user,
                age=age,
                address=address,
                date_of_join=date_of_join,
                images=images
            )
        elif user_type == 'teacher':
            Teacher.objects.create(
                user=user,
                age=age,
                phnoenumber=phonenumber,
                address=address,
                images=images
            )

        # Send email with username and password
        send_mail(
            'Your Account Details',
            f'Username: {username}\nPassword: {password}',
            'admin@example.com',
            [email],
            fail_silently=False,
        )

        success_message = 'Check your email for username and password.'
        return render(request, 'loginpage.html', {'error_message': success_message})
    
    return render(request, 'register.html')

def success(request):
    return render(request, 'success.html')

def aboutus(request):
    return render(request, 'aboutus.html')


def loginpage(request):
    return render (request,'loginpage.html')


def login_view(request):
    error_message = None

    if request.method == 'POST':
        username = request.POST.get('usname')
        password = request.POST.get('passd')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('adminmod')
            elif user.is_staff:
                return redirect('teacher_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            error_message = 'Invalid username or password.'

    return render(request, 'loginpage.html', {'error_message': error_message})


@login_required(login_url='loginpage')
def adminmod(request):
    # Filter new students without courses
    new_students = Student.objects.filter( binary_data=False)

    # Filter new teachers without courses
    new_teachers = Teacher.objects.filter( binary_data=False)

    if not new_students.exists() and not new_teachers.exists():
        # No new students or teachers without courses
        return render(request, 'adminmod.html', {'no_new_users': True})

    return render(request, 'adminmod.html', {
        'no_new_users': False,
        'new_students_count': new_students.count(),
        'new_teachers_count': new_teachers.count()
    })

@login_required(login_url='loginpage')
def teachermod(request):
    return render (request,'teachermod.html')

@login_required(login_url='loginpage')
def studentmod(request):
    return render (request,'studentmod.html')

@login_required(login_url='loginpage')
def lgout(request):
    auth.logout(request)
    return redirect ('loginpage')

@login_required(login_url='loginpage')
def add_course(request):
    return render (request,'add_course.html')

@login_required(login_url='loginpage')
def add_course_(request):
    if request.method == "POST":
        name = request.POST['name']
        fee = request.POST['fee']
        syllabus = request.FILES.get('syllabus')
        duration = request.POST['duration']

        course = Course(name=name, fee=fee, syllabus=syllabus, duration=duration)
        course.save()
        return redirect('course_list')  # Redirect to a course list page after adding

    return render(request, 'add_course.html')

@login_required(login_url='loginpage')
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'course_list.html', {'courses': courses})

@login_required(login_url='loginpage')
def edit_course(request, course_id):
    course = Course.objects.get(id=course_id)
    return render(request, 'edit_course.html', {'course': course})

@login_required(login_url='loginpage')
def edit_course_(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == "POST":
        course.name = request.POST['name']
        course.fee = request.POST['fee']
        course.duration = request.POST['duration']
        if 'syllabus' in request.FILES:
            course.syllabus = request.FILES['syllabus']
        course.save()
        return redirect('course_list')

    return redirect('edit_course')

@login_required(login_url='loginpage')
def delete_course(request, course_id):
    course = Course.objects.get(id=course_id)
    return render(request, 'delete_course.html', {'course': course})

@login_required(login_url='loginpage')
def delete_course_(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == "POST":
        course.delete()
        return redirect('course_list')
    return redirect('delete_course')

@login_required(login_url='loginpage')
def list_fresh_users(request):
    new_students = Student.objects.filter( binary_data=False)
    new_teachers = Teacher.objects.filter( binary_data=False)
    return render(request, 'list_fresh_users.html', {'new_students': new_students, 'new_teachers': new_teachers})

@login_required(login_url='loginpage')
def approve_user(request, user_type, user_id):
    if user_type == 'student':
        user = get_object_or_404(Student, id=user_id)
    elif user_type == 'teacher':
        user = get_object_or_404(Teacher, id=user_id)
    else:
        return redirect('list_new_users')
    
    user.binary_data = True
    user.save()
    return redirect('list_fresh_users')

@login_required(login_url='loginpage')
def list_new_users(request):
    new_students = Student.objects.filter(course__isnull=True,binary_data=True)
    new_teachers = Teacher.objects.filter(course__isnull=True,binary_data=True)
    return render(request, 'list_new_users.html', {'new_students': new_students, 'new_teachers': new_teachers})


@login_required(login_url='loginpage')
def assign_course_(request, user_type, user_id):
    if user_type == 'student':
        user = Student.objects.get(id=user_id)
    elif user_type == 'teacher':
        user = Teacher.objects.get(id=user_id)
    else:
        return redirect('list_new_users')

    if request.method == 'POST':
        course_id = request.POST['course']
        course = Course.objects.get(id=course_id)
        user.course = course
        user.save()
        return redirect('list_new_users')

    courses = Course.objects.all()
    return redirect('assign_course.html')
    # return render(request, 'assign_course.html', {'user': user, 'user_type': user_type, 'courses': courses})

@login_required(login_url='loginpage')
def assign_course(request, user_type, user_id):
    if user_type == 'student':
        user = Student.objects.get(id=user_id)
    elif user_type == 'teacher':
        user = Teacher.objects.get(id=user_id)
    else:
        return redirect('list_new_users')
    courses = Course.objects.all()
    return render(request, 'assign_course.html', {'user': user, 'user_type': user_type, 'courses': courses})
    

@login_required(login_url='loginpage')
def delete_user(request, user_type, user_id):
    if user_type == 'student':
        user = Student.objects.get(id=user_id)
    elif user_type == 'teacher':
        user = Teacher.objects.get(id=user_id)
    else:
        return redirect('list_fresh_users')

    if request.method == 'POST':
        user.delete()
        return redirect('list_fresh_users')

    return render(request, 'confirm_delete_user.html', {'user': user, 'user_type': user_type})

@login_required(login_url='loginpage')
def confirm_delete_user(request, user_type, user_id):
    if user_type == 'student':
        user = Student.objects.get(id=user_id)
    elif user_type == 'teacher':
        user = Teacher.objects.get(id=user_id)
    else:
        return redirect('list_fresh_users')
    return render(request, 'confirm_delete_user.html', {'user': user, 'user_type': user_type})

@login_required(login_url='loginpage')
def users_by_course(request):
    courses = Course.objects.all()
    selected_course_id = request.GET.get('course')

    students = []
    teachers = []

    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        user_id = request.POST.get('user_id')
        new_course_id = request.POST.get('new_course')
        
        new_course = Course.objects.get(id=new_course_id)
        
        if user_type == 'student':
            student = Student.objects.get(id=user_id)
            student.course = new_course
            student.save()
        elif user_type == 'teacher':
            teacher = Teacher.objects.get(id=user_id)
            teacher.course = new_course
            teacher.save()
        
        # Redirect to the same page to reflect the changes
        return redirect('users_by_course')

    if selected_course_id:
        selected_course = Course.objects.get(id=selected_course_id)
        students = Student.objects.filter(course=selected_course)
        teachers = Teacher.objects.filter(course=selected_course)
    else:
        selected_course = None

    return render(request, 'users_by_course.html', {
        'courses': courses,
        'selected_course': selected_course,
        'students': students,
        'teachers': teachers
    })

@login_required(login_url='loginpage')
def view_profile(request, user_type, user_id):
    if user_type == 'student':
        user = Student.objects.get(id=user_id)
    elif user_type == 'teacher':
        user = Teacher.objects.get(id=user_id)
    else:
        return redirect('users_by_course')

    return render(request, 'profile_view.html', {'user': user, 'user_type': user_type})

@login_required(login_url='loginpage')
def delete_user_from_course(request, user_type, user_id):
    if user_type == 'student':
        user = Student.objects.get(id=user_id)
    elif user_type == 'teacher':
        user = Teacher.objects.get(id=user_id)
    else:
        return redirect('users_by_course')

    user.delete()  # Delete the user from the database
    return redirect('users_by_course')

@login_required(login_url='loginpage')
def tenter_attendance(request):
    teachers = Teacher.objects.filter(course__isnull=False)
    return render(request, 'tenter_attendance.html', {'teachers': teachers})

@login_required(login_url='loginpage')
def t_enter_attendance(request):
    if request.method == 'POST':
        teacher_id = request.POST['teacher']
        date = request.POST['date']
        status = request.POST['status']

        teacher = Teacher.objects.get(id=teacher_id)
        attendence = Attendence(date=date, status=status, teacher=teacher)
        attendence.save()

        return redirect('tenter_attendance')

    teachers = Teacher.objects.filter(course__isnull=False)
    return render(request, 'tenter_attendance.html', {'teachers': teachers})

@login_required(login_url='loginpage')
def tattendance_report(request):
    courses = Course.objects.all()
    selected_course = None
    attendance_report = []

    return render(request, 'tattendance_report.html', {
        'courses': courses,
        'selected_course': selected_course,
        'attendance_report': attendance_report
    })

@login_required(login_url='loginpage')
def t_attendance_report(request):
    courses = Course.objects.all()
    selected_course = None
    selected_teacher = None
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    attendance_report = []

    if 'course' in request.GET and request.GET['course']:
        selected_course = Course.objects.get(id=request.GET['course'])

        if 'teacher' in request.GET and request.GET['teacher']:
            selected_teacher = Teacher.objects.get(id=request.GET['teacher'], course=selected_course)

            if start_date and end_date:
                attendances = Attendence.objects.filter(teacher=selected_teacher, date__range=[start_date, end_date], status__isnull=False)

                attendance_report = attendances.values('date', 'status')

    return render(request, 'tattendance_report.html', {
        'courses': courses,
        'selected_course': selected_course,
        'selected_teacher': selected_teacher,
        'start_date': start_date,
        'end_date': end_date,
        'attendance_report': attendance_report
    })


@login_required(login_url='loginpage')
def teacher_dashboard(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
        if teacher.course:
            messages.success(request, f'You have been assigned to the course: {teacher.course.name}.')
        else:
            error_message = 'You are not approved by the admin.'
            return render(request, 'loginpage.html', {'error_message': error_message})
    except Teacher.DoesNotExist:
        error_message =  'You do not have a teacher profile.'
        return render(request, 'loginpage.html', {'error_message': error_message})

    return render(request, 'teacher_dashboard.html', {'teacher': teacher})

@login_required(login_url='loginpage')
def reset_password(request):
    return render(request, 'reset_password.html')

@login_required(login_url='loginpage')
def reset_password_(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        user = request.user

        # Password validation regex: 8 characters, one uppercase, one lowercase, one digit, one special character
        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        
        # Check if the current password is correct
        if user.check_password(current_password):
            if new_password == confirm_password:
                if re.match(password_regex, new_password):
                    user.set_password(new_password)
                    user.save()
                    
                    # Update session hash to prevent logout
                    update_session_auth_hash(request, user)
                    
                    
                    error_message = 'Your password has been reset successfully.'
                    return render(request, 'loginpage.html', {'error_message': error_message})
                else:
                    error_message = 'New password does not meet the minimum requirements.'
                    return render(request, 'reset_password.html', {'error_message': error_message})
            else:
                error_message = 'New passwords do not match.'
                return render(request, 'reset_password.html', {'error_message': error_message})
        else:
            error_message = 'Current password is incorrect.'
            return render(request, 'reset_password.html', {'error_message': error_message})
    
    return redirect('loginpage')

@login_required(login_url='loginpage')
def tstudents_list(request):
    # Get the logged-in teacher
    teacher = Teacher.objects.get(user=request.user)
    
    # Get all students with the same course as the teacher
    students = Student.objects.filter(course=teacher.course)
    
    return render(request, 'tstudents_list.html', {'students': students})

@login_required(login_url='loginpage')
def tstudent_profile(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'tstudent_profile.html', {'student': student})


@login_required(login_url='loginpage')
def tadd_task(request):
    return render(request, 'tadd_task.html')

@login_required(login_url='loginpage')
def tadd_task_(request):
    if request.method == 'POST':
        name = request.POST['name']
        teacher = Teacher.objects.get(user=request.user)
        course = teacher.course  # Get the course associated with the logged-in teacher
        Task.objects.create(name=name, teacher=teacher, course=course)
        return redirect('ttask_list')
    return render(request, 'tadd_task.html')

@login_required(login_url='loginpage')
def ttask_list(request):
    teacher = Teacher.objects.get(user=request.user)
    tasks = Task.objects.filter(teacher=teacher, student=None)
    return render(request, 'ttask_list.html', {'tasks': tasks})

@login_required(login_url='loginpage')
def tdelete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, teacher__user=request.user)
    if request.method == "POST":
        task.delete()
        return redirect('ttask_list')

@login_required(login_url='loginpage')
def senter_attendance(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        return HttpResponseForbidden("You are not authorized to enter attendance.")

    students = Student.objects.filter(course=teacher.course)
    return render(request, 'senter_attendance.html', {'students': students})

@login_required(login_url='loginpage')
def s_enter_attendance(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        return HttpResponseForbidden("You are not authorized to enter attendance.")

    if request.method == 'POST':
        student_id = request.POST['student']
        date = request.POST['date']
        status = request.POST['status']

        student = Student.objects.get(id=student_id)
        if student.course != teacher.course:
            return HttpResponseForbidden("You are not authorized to enter attendance for this student.")

        attendance = Attendence(date=date, status=status, teacher=teacher, student=student)
        attendance.save()

        return redirect('senter_attendance')

    students = Student.objects.filter(course=teacher.course)
    return render(request, 'senter_attendance.html', {'students': students})

@login_required(login_url='loginpage')
def asattendance_report(request):
    courses = Course.objects.all()
    selected_course = None
    selected_student = None
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    attendance_report = []

    return render(request, 'asattendance_report.html', {
        'courses': courses,
        'selected_course': selected_course,
        'selected_student': selected_student,
        'start_date': start_date,
        'end_date': end_date,
        'attendance_report': attendance_report
    })

@login_required(login_url='loginpage')
def as_attendance_report(request):
    courses = Course.objects.all()
    selected_course = None
    selected_student = None
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    attendance_report = []

    if 'course' in request.GET and request.GET['course']:
        selected_course = Course.objects.get(id=request.GET['course'])

        if 'student' in request.GET and request.GET['student']:
            selected_student = Student.objects.get(id=request.GET['student'], course=selected_course)

            if start_date and end_date:
                attendances = Attendence.objects.filter(student=selected_student, date__range=[start_date, end_date], status__isnull=False)

                attendance_report = attendances.values('date', 'status')

    return render(request, 'asattendance_report.html', {
        'courses': courses,
        'selected_course': selected_course,
        'selected_student': selected_student,
        'start_date': start_date,
        'end_date': end_date,
        'attendance_report': attendance_report
    })

@login_required(login_url='loginpage')
def sattendance_report(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        return HttpResponseForbidden("You are not authorized to view attendance reports.")

    courses = Course.objects.filter(id=teacher.course.id)
    selected_course = None
    attendance_report = []

    return render(request, 'sattendance_report.html', {
        'courses': courses,
        'selected_course': selected_course,
        'attendance_report': attendance_report
    })

@login_required(login_url='loginpage')
def s_attendance_report(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        return HttpResponseForbidden("You are not authorized to view attendance reports.")

    courses = Course.objects.filter(id=teacher.course.id)
    selected_course = None
    selected_student = None
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    attendance_report = []

    if 'course' in request.GET and request.GET['course']:
        selected_course = Course.objects.get(id=request.GET['course'])

        if selected_course != teacher.course:
            return HttpResponseForbidden("You are not authorized to view attendance reports for this course.")

        students = Student.objects.filter(course=selected_course)

        if 'student' in request.GET and request.GET['student']:
            selected_student = Student.objects.get(id=request.GET['student'])

            if selected_student.course != selected_course:
                return HttpResponseForbidden("You are not authorized to view attendance reports for this student.")

            if start_date and end_date:
                attendances = Attendence.objects.filter(student=selected_student, date__range=[start_date, end_date]).exclude(status__isnull=True)

                for attendance in attendances:
                    attendance_report.append({
                        'date': attendance.date,
                        'status': attendance.status
                    })

    return render(request, 'sattendance_report.html', {
        'courses': courses,
        'selected_course': selected_course,
        'students': students if selected_course else [],
        'selected_student': selected_student,
        'start_date': start_date,
        'end_date': end_date,
        'attendance_report': attendance_report
    })

@login_required(login_url='loginpage')
def student_dashboard(request):
    try:
        student = Student.objects.get(user=request.user)
        if student.course:
            messages.success(request, f'You have been assigned to the course: {student.course.name}.')
        else:
            error_message = 'You are not approved by the admin or course is not assigned '
            return render(request, 'loginpage.html', {'error_message': error_message})
    except Teacher.DoesNotExist:
        error_message = 'You do not have a teacher profile.'
        return render(request, 'loginpage.html', {'error_message': error_message})

    return render(request, 'student_dashboard.html', {'student': student})

# def student_task_list(request):
#     student = get_object_or_404(Student, user=request.user)
#     tasks = Task.objects.filter(teacher__course=student.course)
#     return render(request, 'student_task_list.html', {'student': student, 'tasks': tasks})

@login_required(login_url='loginpage')
def student_task_list(request):
    student = get_object_or_404(Student, user=request.user)
    tasks = Task.objects.filter(course=student.course)

    # Filter out tasks where a similar task with a student foreign key exists
    filtered_tasks = []
    for task in tasks:
        if not Task.objects.filter(name=task.name, student__isnull=False).exists():
            filtered_tasks.append(task)

    return render(request, 'student_task_list.html', {'student': student, 'tasks': filtered_tasks})

@login_required(login_url='loginpage')
def add_task(request, task_id):
    student = get_object_or_404(Student, user=request.user)
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'add_task.html', {'task': task})

@login_required(login_url='loginpage')
def add_task_(request, task_id):
    student = get_object_or_404(Student, user=request.user)
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        description = request.POST.get('description')
        file = request.FILES.get('file')
        
        Task.objects.create(
            name=task.name,
            description=description,
            file=file,
            student=student,
            course=student.course
        )
        return redirect('student_task_list')

    return render(request, 'add_task.html', {'task': task})

@login_required(login_url='loginpage')
def attendance_summary(request):
    student = get_object_or_404(Student, user=request.user)
    present_count = 0
    absent_count = 0
    return render(request, 'attendance_summary.html', {
        'student': student,
        'present_count': present_count,
        'absent_count': absent_count
    })

@login_required(login_url='loginpage')
def attendance_summary_(request):
    student = get_object_or_404(Student, user=request.user)
    attendance_data = []

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

            # Get all attendance records for the student within the date range where the status is not null
            attendances = Attendence.objects.filter(student=student, date__range=[start_date, end_date]).exclude(status__isnull=True)

            # Prepare the data for each date
            for attendance in attendances:
                attendance_data.append({
                    'date': attendance.date,
                    'status': attendance.status
                })

    return render(request, 'attendance_summary.html', {
        'student': student,
        'attendance_data': attendance_data,
    })

@login_required(login_url='loginpage')
def student_profile(request):
    student = get_object_or_404(Student, user=request.user)
    return render(request, 'student_profile.html', {'student': student})

@login_required(login_url='loginpage')
def edit_student_profile(request):
    student = get_object_or_404(Student, user=request.user)
    return render(request, 'edit_student_profile.html', {'student': student})

@login_required(login_url='loginpage')
def edit_student_profile_(request):
    student = get_object_or_404(Student, user=request.user)

    if request.method == 'POST':
        student = get_object_or_404(Student, user=request.user)

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        age = request.POST.get('age')
        address = request.POST.get('address')
        date_of_join = request.POST.get('date_of_join')
        if 'images' in request.FILES:
            images = request.FILES['images']
        else:
            images = student.images

        # Update Student information
        student.age = age
        student.address = address
        student.date_of_join = date_of_join
        student.images = images
        student.save()

        # Update User information
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.save()

        return redirect('student_profile')

    return render(request, 'edit_student_profile.html', {'student': student})

@login_required(login_url='loginpage')
def teacher_task_list(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    tasks = Task.objects.filter(course=teacher.course, teacher=None)
    return render(request, 'teacher_task_list.html', {'teacher': teacher, 'tasks': tasks})

@login_required(login_url='loginpage')
def teacher_attendance_summary(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    present_count = 0
    absent_count = 0
    # present_count = Attendence.objects.filter(teacher=teacher, status='Present').count()
    # absent_count = Attendence.objects.filter(teacher=teacher, status='Absent').count()
    return render(request, 'teacher_attendance_summary.html', {
        'teacher': teacher,
        'present_count': present_count,
        'absent_count': absent_count
    })

@login_required(login_url='loginpage')
def teacher_attendance_summary_with_dates(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    attendance_report = []

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

            attendances = Attendence.objects.filter(teacher=teacher, date__range=[start_date, end_date]).exclude(status__isnull=True)

            for attendance in attendances:
                attendance_report.append({
                    'date': attendance.date,
                    'status': attendance.status
                })

    return render(request, 'teacher_attendance_summary.html', {
        'teacher': teacher,
        'attendance_report': attendance_report
    })


def home(request):
    return render(request, 'home.html')


def contact(request):
    return render(request, 'contact.html')

@login_required(login_url='loginpage')
def page4(request):
    return render(request, 'page4.html')

@login_required(login_url='loginpage')
def teacher_profile(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    return render(request, 'teacher_profile.html', {'teacher': teacher})

@login_required(login_url='loginpage')
def edit_teacher_profile(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    return render(request, 'edit_teacher_profile.html', {'teacher': teacher})

@login_required(login_url='loginpage')
def edit_teacher_profile_(request):
    teacher = get_object_or_404(Teacher, user=request.user)

    if request.method == 'POST':
        teacher = get_object_or_404(Teacher, user=request.user)

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        age = request.POST.get('age')
        address = request.POST.get('address')
        phnoenumber = request.POST.get('phnoenumber')
        if 'images' in request.FILES:
            images = request.FILES['images']
        else:
            images = teacher.images

        # Update teacher information
        teacher.age = age
        teacher.address = address
        teacher.phnoenumber = phnoenumber
        teacher.images = images
        teacher.save()

        # Update User information
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.save()

        return redirect('teacher_profile')

    return render(request, 'edit_teacher_profile.html', {'teacher': teacher})

@login_required(login_url='loginpage')
def student_tasks(request):
    student = Student.objects.get(user=request.user)
    tasks = Task.objects.filter(student=student)
    return render(request, 'student_tasks.html', {'tasks': tasks})