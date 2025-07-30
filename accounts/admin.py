from django.contrib import admin
from django.utils.html import format_html
from .models import Account, UserProfile
from django.contrib.auth.admin import UserAdmin
# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'date_joined', 'last_login', 'is_admin',
                    'is_staff', 'is_active', 'is_superadmin', 'phone_number')
    list_display_links = ('email', 'username', 'first_name', 'last_name', 'phone_number') # This will make the email and username clickable in the admin panel

    readonly_fields = ('last_login', 'date_joined') # This will make the last login and date joined Read-Only in the admin panel

    ordering = ('-date_joined',)

    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone_number') # This will make the search bar in the admin panel
    filter_horizontal = ()
    list_filter = () # This is used to make the password Read-Only in the admin panel
    fieldsets = ()
    
class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        if object.profile_picture and hasattr(object.profile_picture, 'url'):
            return format_html('<img src="{}" width="30" height="30" style="border-radius: 50%;">', object.profile_picture.url)
        else:
            return format_html('<img src="/media/userprofile/default.jpg" width="30" height="30" style="border-radius: 50%;">')
    # This is a custom method for the Django admin. 
    # It takes a UserProfile object and returns an HTML <img> tag 
    # displaying the user's profile picture as a small, rounded image in the admin interface.
    def full_name(self, object):
        # This method returns the full name of the user associated with the UserProfile object.
        return f'{object.user.first_name} {object.user.last_name}'
    
    full_name.short_description = 'Full Name'
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user', 'full_name', 'city', 'state', 'country')

admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

