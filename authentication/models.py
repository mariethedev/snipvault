

from django.db import models
from django.contrib.auth.models import PermissionsMixin, UserManager, AbstractBaseUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
from django.apps import apps
import jwt
from django.conf import settings
from datetime import datetime,timedelta
from django.core.exceptions import ValidationError


class MyUserManager(UserManager):         

    def _create_user(self, email, password, **extra_fields):    
        if not email:
                raise ValidationError("Ensure the given email has been set")

        email = self.normalize_email(email)                         

        user = self.model(email=email, **extra_fields)

        user.password = make_password(password)                 
        user.save(using=self._db)                               
        return user
 
    def create_user(self, email, password=None, **extra_fields):        
        
        extra_fields.setdefault("is_staff", False)                                 
        extra_fields.setdefault("is_superuser", False)
        
        if not email:
            raise ValidationError("Ensure the given email has been set")
    

        return self._create_user(email, password, **extra_fields)         

    def create_superuser(self, email, password=None, **extra_fields):         
        extra_fields.setdefault("is_staff", True)                                 
        extra_fields.setdefault("is_superuser", True)
        
        if not email:
                raise ValidationError("Ensure the given email has been set")

        if extra_fields.get('is_staff') is not True:
            raise ValidationError("Superuser must have is_staff=True")
        if extra_fields.get('is_superuser') is not True:
            raise ValidationError("Superuser must have is_superuser=True")

        return self._create_user(email, password, **extra_fields)              
    

class User(AbstractBaseUser, PermissionsMixin): 
    
    
    AUTH_PROVIDERS =(
         ('email', 'Email'),
         ('google', 'Google'),
         ('github', 'Github')
    )  

    firstname = models.CharField(_("Firstname"), max_length = 64,)
    lastname = models.CharField(_("lastname"), max_length = 64)
    email = models.EmailField(_("email address"), blank=False, unique = True)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    auth_provider= models.CharField(max_length=20, choices= AUTH_PROVIDERS, default='email')
    is_staff = models.BooleanField(_("staff status"), default=False,)
    is_active = models.BooleanField(_("active"), default=True, )
    

    objects = MyUserManager() 

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = "email" 
    REQUIRED_FIELDS = []




 


