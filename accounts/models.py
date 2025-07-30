from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# Create your models here.
class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, phone_number, password=None):
        if not email:
            raise ValueError("Email Address is REQUIRED!😑")
        if not username:
            raise ValueError("Username is REQUIRED!😑")
        if not first_name:
            raise ValueError("First Name you MUST have!😑")

        if not last_name:
            raise ValueError("Last Name you MUST have!😑")
        
        user = self.model(
            email=self.normalize_email(email), # will lowercase the email
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone_number = phone_number,
        )
        # once this is done, we can set up the password
        user.set_password(password)
        user.save(using=self._db) # using the default database
        return user
    # this method is used to create a user



    def create_superuser(self, email, username, first_name, last_name, phone_number, password=None):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            password=password,
            last_name = last_name,
            phone_number = phone_number,
        )
        user.is_superadmin = True
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user



class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    # Charfield stores strings which you can use to store usernames
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=100, unique=True)


    # required status fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    # log in methods
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'phone_number']

    def __str__(self):
        return self.email

    def full_name(self):
        return f'{self.first_name.capitalize()} {self.last_name.capitalize()}'

    def has_perm(self, perm, obj=None): # must mention when creating custom user models
        return self.is_admin
    
    def has_module_perms(self, add_label): # must always be true
        return True
    objects = MyAccountManager() # this is the custom user manager we created above

# making a user profile model for editing the profile and extend the functionality scope
class UserProfile(models.Model):
    # only may have one account for this key, "only one profile for one user"
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    address_line_1 = models.CharField(blank=True, max_length=67)
    address_line_2 = models.CharField(max_length=67, blank=True)
    profile_picture = models.ImageField(blank=True, upload_to='userprofile/', default='userprofile/default.jpg')  # Path relative to your MEDIA_ROOT
    city = models.CharField(max_length=67, blank=True)
    state = models.CharField(max_length=67, blank=True)
    country = models.CharField(max_length=67, blank=True)

    def __str__(self):
        return self.user.first_name
    
    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'
