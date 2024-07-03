from django.contrib import admin
from .models import UserAccount, Profile


class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','email','phone']

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name','gender','country']
    list_filter = ['date']

    
# Register your models here.
admin.site.register(UserAccount, UserAdmin)
admin.site.register(Profile, ProfileAdmin)