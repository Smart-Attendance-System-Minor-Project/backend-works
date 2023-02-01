import ast

teacher_email_list = ['pratikdahal05@gmail.com', 'imrajeshneupane@gmail.com', 'jharahul968@gmail.com']

def returnPresence(record):
    attendance_record = ast.literal_eval(record)
    total_students = len(attendance_record)
    total_presence = 0
    for i in attendance_record:
        if i['presence'] == 'present':
            total_presence += 1
    
    try:
        percentage_present = (total_presence/total_students)*100
        return percentage_present
    
    except Exception as e:
        error_message = e.__class__.__name__
        return error_message