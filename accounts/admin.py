from django.contrib import admin
from .models import Account
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
    

admin.site.register(Account, AccountAdmin)
