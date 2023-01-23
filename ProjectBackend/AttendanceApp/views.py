from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from .validation import teacher_email_list
from rest_framework.response import Response
from rest_framework import status
from .models import Teacher
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
        print(f"type(registration details) =  {type(registration_details)} ")
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
    registration_details = request.data
    username = registration_details['username']
    password = registration_details['password']
    teachers = Teacher.objects.all()
    json_data_success = json.dumps({'success': 'welcome user'})
    json_data_failure = json.dumps({'failure': 'invalid username or password'})
    for teacher in teachers:
        if username == teacher.username and password == teacher.password:
            return Response(data= json_data_success, status= status.HTTP_200_OK)

    return Response(data = json_data_failure, status = status.HTTP_403_FORBIDDEN)


    


    