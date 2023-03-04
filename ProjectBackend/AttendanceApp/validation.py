teacher_email_list = ['pratikdahal05@gmail.com', 'imrajeshneupane@gmail.com', 'jharahul968@gmail.com', '076bct055.rajesh@pcampus.edu.np']

def isValidEmail(email):
    try:
        domain = email.split('@')

        if domain[1] != 'pcampus.edu.np':
            return False
        
        first_name, last_name = domain[0].split('.')
        if first_name.isalpha() == True and last_name.isalpha() == True:
            return True
        
        else:
            return False
        
    except ValueError:
        return False