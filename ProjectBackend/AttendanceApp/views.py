from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .validation import teacher_email_list, returnPresence
from rest_framework.response import Response
from rest_framework import status
from .models import Teacher, OneTimePassword, AttendanceRecord
import random, time, ast, json
from django.core.mail import send_mail
from django.db import IntegrityError

#ast is an abstract syntax tree and it is used to convert one data type to the other

# Create your views here.
def helloUser(request):
    return HttpResponse("Hello user. This is a test site for WellAttend App.")

@csrf_exempt
@api_view(['POST'])
def teacherRegistration(request):
    if request.method == 'POST':
        registration_details = request.data
        # registration_details = request.body
        # print(f"registration details = {registration_details}")
        # registration details = b'{"username": "sharma", "email": "sharma", "password": "sharma", "confirm_password": "sharma"}'
        # print(f"type(registration details) =  {type(registration_details)} ")
        #type(registration details) =  <class 'bytes'>
        # print(f"request.data = {request.data}")
        # request.data = {'username': 'sharma', 'email': 'sharma', 'password': 'sharma', 'confirm_password': 'sharma'}
        # print("type(request.data) = ", type(request.data))
        # type(request.data) =  <class 'dict'>
        # strng = str(request.body)
        # print(f"strng = {strng} and type(strng) = {type(strng)} ")
        # strng = b'{"username": "sharma", "email": "sharma", "password": "sharma", "confirm_password": "sharma"}' and type(strng) = <class 'str'>
        # registration_details = json.loads(registration_details)
        # print(f"type(registration details) =  {type(registration_details)} ")
        # type(registration details) =  <class 'dict'>
        username = registration_details['username']
        email = registration_details['email']
        password = registration_details['password']
        confirm_password = registration_details['confirm_password']
        full_name = registration_details['full_name']
        print(f"username = {username} and type(username) = {type(username)}")

        if email not in teacher_email_list:
            # return_json = json.dumps({'status_code':'403','error':'Please register with your college mail id or contact department.'})
            return_json = {'status_code':'403','error':'Please register with your college mail id or contact department.'}
            # print("here")
            return Response(data = return_json, status= status.HTTP_403_FORBIDDEN, content_type= "application/json")
        if password != confirm_password:
            return_json = json.dumps({'error':'The entered passwords do not match.'})
            return Response(data = return_json, status= status.HTTP_400_BAD_REQUEST)
        
        try:
            # print("inside the try block")
            teacher = Teacher(username = username, email = email, password = password, full_name = full_name)
            teacher.save()

        except IntegrityError:
            # print("Inside the integrity error")
            failure_data = {"message": "Username already exists. Please enter a unique username."}
            return Response(data = failure_data, status= status.HTTP_409_CONFLICT)
       
        return HttpResponse("success")

@csrf_exempt
@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        login_details = request.data
        username = login_details['username']
        password = login_details['password']
        try:
            teacher = Teacher.objects.get(username = username, password = password)
        except:
            teacher = None
        print("teachers = ", teacher)
        if teacher is not None:
                json_data_success = {'success': f'welcome {teacher.full_name} sir'}
                return Response(data= json_data_success, status= status.HTTP_200_OK)
        json_data_failure = {'failure': 'invalid username or password'}
        return Response(data = json_data_failure, status = status.HTTP_403_FORBIDDEN)

@csrf_exempt
@api_view(['POST'])
def forgotPassword(request):
    if request.method == 'POST':
        email = request.data['email']
        # print("email = ", email, "type(email) = ", type(email))
        email_dct = {'email': email}
        all_user_emails = Teacher.objects.values('email')

        # for i in all_user_emails:
        #     print(i)
        #     print(type(i))
        # print(all_user_emails)
        if email_dct not in all_user_emails:
            return_data = {'failure': 'Please enter your campus email or contact the department.'}
            return Response(data = return_data, status= status.HTTP_403_FORBIDDEN)
        
        #this needs to modified..........
        # global otp
        OneTimePassword.objects.filter(email = email).delete()
        otp = random.randint(100000, 999999)
        print("otp  = ", otp)
        OneTimePassword.objects.create(email = email, otp = otp, time = int(time.time()))
        send_mail("Password Reset", f"Your OTP is {otp}", 'mail.ioehub@gmail.com', [f'{email}'], fail_silently= False,)
        #if fail_silently is set to True, you'll get no log of error messages.
        return_data = {'success': f'An otp has been sent to {email}. Please enter the otp and reset your password.'}
        return Response(data = return_data, status= status.HTTP_200_OK)
        #the user is directed to /otp_validation after this

@csrf_exempt
@api_view(['POST'])
def validateOTP(request):
    if request.method == 'POST':
        entered_email = request.data['email']
        entered_otp = request.data['otp']
        try:
            otp_data = OneTimePassword.objects.get(email = entered_email)
            current_time = int(time.time())
            otp = otp_data.otp
            time_duration = current_time - int(otp_data.time)
            if time_duration > 120:
                failure_message = {'message': 'otp expired'}
                otp_data.delete()
                return Response(data = failure_message, status= status.HTTP_410_GONE)

            if entered_otp == otp:
                success_message = {'message': 'otp verified successfully.'}
                otp_data.delete()
                return Response(data = success_message, status= status.HTTP_200_OK)
            
            else:
                failure_message = {'message': 'invalid otp.'}
                return Response(data = failure_message, status= status.HTTP_401_UNAUTHORIZED)


        except OneTimePassword.DoesNotExist:
            failure_message = {'message': f'OTP was not requested by {entered_email} or it expired.'}
            return Response(data = failure_message, status = status.HTTP_410_GONE)


@csrf_exempt
@api_view(['POST'])
def passwordReset(request):
    if request.method == 'POST':
        entered_email = request.data['email']
        entered_password = request.data['password']
        confirm_password = request.data['confirm_password']
        if entered_password != confirm_password:
            failure_message = {'failure': 'the entered password do not match.'}
            return Response(data = failure_message, status= status.HTTP_403_FORBIDDEN)
        
        

        #security concern. Hash these password
        try:
            teacher = Teacher.objects.get(email = entered_email)
            teacher.password = entered_password
            teacher.save(update_fields = ['password'])
        
        except Teacher.DoesNotExist:
            failure_message = {'failure': 'invalid email. Please enter your college email or contact the department.'}
            return Response(data = failure_message, status= status.HTTP_403_FORBIDDEN)
            

        success_message = {'success': 'password changed successfully'}
        return Response(data = success_message, status= status.HTTP_200_OK)

@api_view(['GET'])
def seeUsers(request):
    teacher = Teacher.objects.all()
    teacher_string = '' 

    for i in teacher:
        teacher_string += str(i.username) + "  " + str(i.full_name)+ '<br>'
    return HttpResponse(teacher_string)

@api_view(['POST'])
def viewClasses(request):
    username = request.data['username']
    try:
        teacher = Teacher.objects.get(username = username)
        try:
            classes = ast.literal_eval(teacher.classes)
            return Response(data = classes, status= status.HTTP_200_OK)

        except SyntaxError:
            classes = list(teacher.classes)
            return Response(data = classes, status= status.HTTP_200_OK)

    
    except Teacher.DoesNotExist:
        failure_message = {'failure': f'invalid username. Teacher with username {username} does not exist.'}
        return Response(data = failure_message, status= status.HTTP_403_FORBIDDEN)



#login should be required for this
@api_view(['POST'])
def addClass(request):
    if request.method == 'POST':
        class_details = request.data
        #username will be sent by the frontend
        username = class_details['username']
        batch = class_details['batch']
        faculty = class_details['faculty']
        subject = class_details['subject']
        class_type = class_details['class_type']
        section = class_details['section']

        class_name = batch + faculty + section
        
        try:
            teacher = Teacher.objects.get(username = username)
            class_dct = {'subject': subject, 'class_name': class_name, 'class_type': class_type} 
            # classes = teacher.classes
            # print(f"classes = {classes} and type(classes) = {type(classes)}")
            try:
                classes = ast.literal_eval(teacher.classes)
            
            except SyntaxError:
                classes = list(teacher.classes)
            
            if class_dct not in classes:
                classes.append(class_dct)
                classes = str(classes)
                teacher.classes = classes
                # teacher.classes = ""
                teacher.save()
                success_message = {'message': f'class {class_name} added successfully.'}
                return Response(data = success_message, status = status.HTTP_200_OK)
            
            else:
                message = {'message': f'class {class_name} - {subject} - {class_type} already exists.'}
                return Response(data = message, status = status.HTTP_208_ALREADY_REPORTED)

        
        except Teacher.DoesNotExist:
            failure_message = {'message': f'teacher with username {username} does not exist.'}
            return Response(data = failure_message, status= status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
def viewOTP(request):
    otps = OneTimePassword.objects.all()
    otp_list = []
    for i in otps:
        otp_list.append([i.email, i.time, i.otp])

    return HttpResponse(f"OTPs are printed as {otp_list}")

@api_view(['POST'])
def saveRecord(request):
    if request.method == 'POST':
        record_details = request.data
        teacher_username = record_details['username']
        class_name = record_details['class_name'] #for example 076bctcd
        class_type = record_details['class_type'] #lecture or practical
        subject = record_details['subject'] 
        attendance_record = record_details['attendance_record']
        print("attendance_record = ", attendance_record, "type(attendance_record) = ", type(attendance_record))
        try:
            print("hola mundo")
            record = AttendanceRecord.objects.get(teacher_username = teacher_username, class_name = class_name, class_type = class_type, subject = subject)
            print("hola mundo")
            print("record = ", record)
            print("record.attendance_record = ", record.attendance_record)
            print("type of record.attendance_record = ", type(record.attendance_record))

            record.attendance_record = json.dumps(record.attendance_record) + json.dumps(attendance_record)
            record.save()
            message = {'message': 'Attendance taken successfully.'}
            return Response (data = message, status= status.HTTP_200_OK)
                       
        except AttendanceRecord.DoesNotExist as err:
            error_name = err
            print("error = ", error_name)
            AttendanceRecord.objects.create(teacher_username = teacher_username, class_name = class_name, class_type = class_type, subject = subject, attendance_record = attendance_record)
            message = {'message': 'Attendance taken successfully.'}
            return Response(data = message, status= status.HTTP_403_FORBIDDEN)
            
