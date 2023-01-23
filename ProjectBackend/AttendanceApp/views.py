from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from .validation import teacher_email_list
from rest_framework.response import Response
from rest_framework import status
from .models import Teacher
import random
from django.core.mail import send_mail
# Create your views here.
def helloUser(request):
    return HttpResponse("Welcome user.")

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
        
        if email not in teacher_email_list:
            # return_json = json.dumps({'status_code':'403','error':'Please register with your college mail id or contact department.'})
            return_json = {'status_code':'403','error':'Please register with your college mail id or contact department.'}
            # print("here")
            return Response(data = return_json, status= status.HTTP_403_FORBIDDEN, content_type= "application/json")
        if password != confirm_password:
            return_json = json.dumps({'error':'The entered passwords do not match.'})
            return Response(data = return_json, status= status.HTTP_400_BAD_REQUEST)
        print("good")
        teacher = Teacher(username = username, email = email, password = password)
        teacher.save()
       
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
        json_data_success = {'success': f'welcome {teacher.first_name} sir'}
        json_data_failure = {'failure': 'invalid username or password'}
        if teacher is not None:
                return Response(data= json_data_success, status= status.HTTP_200_OK)
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
        
        global otp
        otp = round(random.random()*10**6)
        print("otp  = ", otp)
        send_mail("Password Reset", f"Your OTP is {otp}", 'mail.ioehub@gmail.com', ['fofehi6850@moneyzon.com'] , fail_silently= False,)
        #if fail_silently is set to True, you'll get no log of error messages.
        return_data = {'success': f'An otp has been sent to {email}. Please enter the otp and reset your password.'}
        return Response(data = return_data, status= status.HTTP_200_OK)
        #the user is directed to /otp_validation after this

@csrf_exempt
@api_view(['POST'])
def validateOTP(request):
    if request.method == 'POST':
        entered_otp = int(request.data['otp'])
        # print("entered otp = ", entered_otp)
        # print("type(entered otp) = ", type(entered_otp))
        if entered_otp == otp:
            success_message = {'success': 'Email verified successfully.'}
            return Response(data = success_message, status = status.HTTP_200_OK)
        
        failure_message = {'failure': 'Invalid OTP.'}
        return Response(data = failure_message, status= status.HTTP_403_FORBIDDEN)
        #the user is directed to password reset after this

@csrf_exempt
@api_view(['POST'])
def passwordReset(request):
    if request.method == 'POST':
        entered_email = request.data['email']
        entered_password = request.data['password']
        #security concern. Hash these password
        teacher = Teacher.objects.get(email = entered_email)
        teacher.password = entered_password
        teacher.save(update_fields = ['password'])
        success_message = {'success': 'password changed successfully'}
        return Response(data = success_message, status= status.HTTP_200_OK)



    


    