from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import RecordSerializer
from rest_framework.renderers import JSONRenderer
from .models import Teacher, OneTimePassword, AttendanceRecord
import random, time, ast, json
from django.core.mail import send_mail
from django.db import IntegrityError
from .validation import teacher_email_list, isValidEmail
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from django.contrib.auth.hashers import make_password
from datetime import datetime
#ast is an abstract syntax tree and it is used to convert one data type to the other

# Create your views here.
def helloUser(request):
    return HttpResponse("Hello user. This is a test site for WellAttend App.")

@csrf_exempt
@api_view(['POST'])
def teacherRegistration(request):
    registration_details = request.data
    email = registration_details['email']
    if email not in teacher_email_list and not isValidEmail(email):
        message = {'error':'Please register with your college mail id or contact department.'}
        return Response(data = message, status= status.HTTP_403_FORBIDDEN, content_type= "application/json")
    
    OneTimePassword.objects.filter(email = email).delete()
    otp = random.randint(100000, 999999)
    OneTimePassword.objects.create(email = email, otp = otp, time = int(time.time()))
    send_mail("Verify Email", f"Your OTP is {otp}. Please use it to verify your email for registration.", 'mail.ioehub@gmail.com', [f'{email}'], fail_silently= False,)
    message = {'success': 'otp sent successfully.'}
    return Response (data = message, status= status.HTTP_200_OK)

       
@csrf_exempt
@api_view(['POST'])
def createUser(request):
    registration_details = request.data
    username = registration_details['username']
    email = registration_details['email']
    password = registration_details['password']
    confirm_password = registration_details['confirm_password']
    full_name = registration_details['full_name']

    if email not in teacher_email_list and not isValidEmail(email):
        message = {'error':'Please register with your college mail id or contact department.'}
        return Response(data = message, status= status.HTTP_403_FORBIDDEN, content_type= "application/json")
    
    if password != confirm_password:
        message = {'error':'The entered passwords do not match.'}
        return Response(data = message, status= status.HTTP_400_BAD_REQUEST)
    try:
        # print("inside the try block")
        hashed_password = make_password(password,salt=username)
        Teacher.objects.create(username = username, email = email, password = hashed_password, full_name = full_name)
        teacher = Teacher.objects.get(username = username, email = email, password = hashed_password, full_name = full_name)
        
        refresh = RefreshToken.for_user(teacher)
        print("refresh = ", refresh, "type = ", type(refresh))
        message = {'success': f'Successfully registered {teacher.full_name} sir', 'refresh':str(refresh), 'access':str(refresh.access_token)}
        jwt_token = str(refresh.access_token)
        jwt_payload = jwt.decode(jwt_token, verify=False)
        print("jwt-payload = ", jwt_payload)
        print("request.user = ", request.user)
        return Response(data = message, status= status.HTTP_200_OK)
        

    except IntegrityError as exc:
        exc.__class__.__name__
        print(f"Error = {exc.__class__.__name__}.")
        print("exc = ", exc)
        if 'username' in str(exc):
            message = {'Error: Username already exists'}
        
        elif 'email' in str(exc):
            message = {'Error: An account already exists with this email.'}
        
        else:
            message = {'Error: Unknown Integrity Error.'}

        return Response(data = message, status= status.HTTP_409_CONFLICT)


@csrf_exempt
@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        login_details = request.data
        username = login_details['username']
        password = login_details['password']
        hashed_password = make_password(password, salt=username)
        try:
            teacher = Teacher.objects.get(username = username, password = hashed_password)
        except:
            teacher = None
        
        if teacher is not None:
            refresh = RefreshToken.for_user(teacher)
            print("refresh = ", refresh, "type = ", type(refresh))
            message = {'success': f'welcome {teacher.full_name} sir', 'refresh':str(refresh), 'access':str(refresh.access_token)}
            jwt_token = str(refresh.access_token)
            jwt_payload = jwt.decode(jwt_token, verify=False)
            print("jwt-payload = ", jwt_payload)
            print("request.user = ", request.user)
            return Response(data= message, status= status.HTTP_200_OK)
        
        else:
            message = {'error': 'Invalid Credentials'}
            return Response(data = message, status = status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
@csrf_exempt
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
            message = {'error': 'Please enter your campus email or contact the department.'}
            return Response(data = message, status= status.HTTP_403_FORBIDDEN)
        
        #this needs to modified..........
        # global otp
        OneTimePassword.objects.filter(email = email).delete()
        otp = random.randint(100000, 999999)
        print("otp  = ", otp)
        OneTimePassword.objects.create(email = email, otp = otp, time = int(time.time()))
        send_mail("Password Reset", f"Your OTP is {otp}. Please use it to verify your email.", 'mail.ioehub@gmail.com', [f'{email}'], fail_silently= False,)
        #if fail_silently is set to True, you'll get no log of error messages.
        message = {'success': f'An otp has been sent to {email}. Please enter the otp and reset your password.'}
        return Response(data = message, status= status.HTTP_200_OK)
        #the user is directed to /otp_validation after this

@api_view(['POST'])
@csrf_exempt
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
                message = {'error': 'otp expired'}
                otp_data.delete()
                return Response(data = message, status= status.HTTP_410_GONE)

            if entered_otp == otp:
                message = {'success': 'otp verified successfully.'}
                otp_data.delete()
                return Response(data = message, status= status.HTTP_200_OK)
            
            else:
                message = {'error': 'invalid otp.'}
                return Response(data = message, status= status.HTTP_401_UNAUTHORIZED)


        except OneTimePassword.DoesNotExist:
            message = {'error': f'OTP was not requested by {entered_email} or it expired.'}
            return Response(data = message, status = status.HTTP_410_GONE)


@api_view(['POST'])
@csrf_exempt
def passwordReset(request):
    if request.method == 'POST':
        entered_email = request.data['email']
        entered_password = request.data['password']
        confirm_password = request.data['confirm_password']
        if entered_password != confirm_password:
            message = {'error': 'the entered password do not match.'}
            return Response(data = message, status= status.HTTP_403_FORBIDDEN)
        
        try:
            teacher = Teacher.objects.get(email = entered_email)
            hashed_password = make_password(entered_password, salt = teacher.username)
            teacher.password = hashed_password
            teacher.save(update_fields = ['password'])
            success_message = {'success': 'password changed successfully'}
            return Response(data = success_message, status= status.HTTP_200_OK)
        
        except Teacher.DoesNotExist:
            failure_message = {'error': 'invalid email. Please enter your college email or contact the department.'}
            return Response(data = failure_message, status= status.HTTP_403_FORBIDDEN)
            



@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
        failure_message = {'error': f'invalid username. Teacher with username {username} does not exist.'}
        return Response(data = failure_message, status= status.HTTP_403_FORBIDDEN)



#login should be required for this
@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
                success_message = {'success': f'class {class_name} added successfully.'}
                return Response(data = success_message, status = status.HTTP_200_OK)
            
            else:
                message = {'error': f'class {class_name} - {subject} - {class_type} already exists.'}
                return Response(data = message, status = status.HTTP_208_ALREADY_REPORTED)

        except Teacher.DoesNotExist:
            failure_message = {'error': f'teacher with username {username} does not exist.'}
            return Response(data = failure_message, status= status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def viewOTP(request):
    otps = OneTimePassword.objects.all()
    otp_list = []
    for i in otps:
        otp_list.append([i.email, i.time, i.otp])

    return HttpResponse(f"OTPs are printed as {otp_list}")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def saveRecord(request):
    if request.method == 'POST':
        record_details = request.data
        teacher_username = record_details['username']
        class_name = record_details['class_name'] #for example 076bctcd
        class_type = record_details['class_type'] #l or p
        subject = record_details['subject'] 
        attendance_record = record_details['attendance_record']
        print("attendance_record = ", attendance_record, "type(attendance_record) = ", type(attendance_record))
        # type(attendance_record) =  <class 'dict'>
        try:
            # print("hola mundo")
            record = AttendanceRecord.objects.get(teacher_username = teacher_username, class_name = class_name, class_type = class_type, subject = subject)
            # record =  AttendanceRecord object (10)
            # print("hola mundo")
            # print("record = ", record)
            # print("record.attendance_record = ", record.attendance_record)
            # print("type of record.attendance_record = ", type(record.attendance_record))
            # type of record.attendance_record =  <class 'str'>
            #json.dumps(x) = x lai json string ma dump gar vai
            date = next(iter(attendance_record.keys()))
            record.attendance_record[date] = attendance_record[date]
            print("record.attendance_record = ", record.attendance_record)
            record.save()
            message = {'success': 'Attendance taken successfully.'}
            return Response (data = message, status= status.HTTP_200_OK)
                       
        except AttendanceRecord.DoesNotExist as err:
            error_name = err
            print("error = ", error_name)
            AttendanceRecord.objects.create(teacher_username = teacher_username, class_name = class_name, class_type = class_type, subject = subject, attendance_record = attendance_record)
            message = {'success': 'Attendance taken successfully.'}
            return Response(data = message, status= status.HTTP_200_OK)
            

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getRecords(request):
    if request.method == 'POST':
        record_details = request.data
        username = record_details['username']
        class_only = record_details.get('class_only')

        try:
            attendance_record_queryset = AttendanceRecord.objects.filter(teacher_username = username)
            attendance_record_serialized= RecordSerializer(attendance_record_queryset, many = True)
            attendance_record_bytes = JSONRenderer().render(attendance_record_serialized.data)

            attendance_record_string = attendance_record_bytes.decode('utf-8')
            attendance_record_json_object = json.loads(attendance_record_string)
            attendance_record_json_string = json.dumps(attendance_record_json_object)
            print(f"json_record = {attendance_record_json_string} and its type is {type(attendance_record_json_string)}")
            print(f"json_record = {attendance_record_json_object} and its type is {type(attendance_record_json_object)}")

            if class_only == "True":
                del attendance_record_json_object['attendance_record']
                del attendance_record_json_object['teacher_username']
            
            return Response(data = attendance_record_json_object, status= status.HTTP_200_OK)

        except AttendanceRecord.DoesNotExist as err:
            error_name = err
            print("error = ", error_name)
            message = {'error': f'Error! {error_name}. No data exists for the given details.'}
            return Response(message, status = status.HTTP_204_NO_CONTENT)


# @authentication_classes([JWTAuthentication, ])
@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def seeUsers(request):
    print("hello world")
    teacher = Teacher.objects.all()
    teacher_string = '' 

    for i in teacher:
        teacher_string += str(i.username) + "  " + str(i.full_name)+ '<br>'
    print("request.user = ", request.user)
    return HttpResponse(teacher_string)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def warnStudents(request):
    details = request.data
    email = details['email']
    subject = details['subject']
    message = details.get('message')
    message = '' if message == None else message
    total_absent = details.get('total_absent')
    total_class = details.get('total_class')
    student_name = details.get('student_name')
    subject_name = details.get('subject_name')
    class_name = details.get('class_name')
    presence_percent = round((int(total_class) - int(total_absent))*100/ int(total_class), 2)
    email_body = f'Dear {student_name}, \n\nThis is to inform you that your presence in the class {class_name}-{subject_name} is poor. Please attend class regularly. \n \nTotal class = {total_class} \nTotal absent = {total_absent} \nPresence percentage = {presence_percent}%\n \n' + message + '\n\nThis is an automated email. Please do not reply.'
    send_mail(subject, email_body, 'mail.ioehub@gmail.com', [f'{email}'], fail_silently= False,)

    return_message = {'success': 'student warned successfully'}
    return Response(data = return_message, status= status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def returnRecentDate(request):
    record_details = request.data
    teacher_username = record_details['username']
    class_name = record_details['class_name'] #for example 076bctcd
    class_type = record_details['class_type'] #l or p
    subject = record_details['subject'] 

    class_details = AttendanceRecord.objects.get(teacher_username = teacher_username, class_name = class_name, class_type = class_type, subject = subject)

    attendance_records = class_details.attendance_record
    dates = list(attendance_records.keys()) 

    # Convert each string date to a datetime object
    datetime_dates = [datetime.strptime(date, "%m/%d/%Y") for date in dates]

    # Find the latest date
    latest_date = max(datetime_dates)

    # Convert the latest date back to string format
    latest_date_str = latest_date.strftime("%m/%d/%Y")

    print("Latest date:", latest_date_str)
    message = {'latest_date': latest_date_str}
    return Response(data = message, status= status.HTTP_200_OK)

    


    