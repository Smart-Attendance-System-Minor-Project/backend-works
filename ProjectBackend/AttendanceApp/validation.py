teacher_email_list = ['pratikdahal05@gmail.com', 'imrajeshneupane@gmail.com', 'jharahul968@gmail.com', '076bct055.rajesh@pcampus.edu.np']

def returnPresence(record):
    print(f"record = {record} and type(record) = {type(record)}")
    # attendance_record = json.dumps(record)
    # print(f"attendance_record = {attendance_record} and type(attendance_record) = {type(attendance_record)}")
    total_students = len(record)
    total_presence = 0
    for i in record.values():
        if i.lower() == 'p':
            total_presence += 1
    
    try:
        percentage_present = round((total_presence/total_students)*100, 2)
        return percentage_present
    
    except Exception as e:
        error_message = e.__class__.__name__
        return error_message