from django.contrib.auth.base_user import BaseUserManager

class TeacherManager(BaseUserManager):

    def create_user(self, username,email, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username,email=email, **extra_fields)
        user.set_password(password)
        user.is_active=True
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username,email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # extra_fields.setdefault('is_admin', True)
        user = self.create_user(username,email, password=password, **extra_fields)
        user.save()
        return user

    def get_by_natural_key(self, username):
        return self.get(username = username)
