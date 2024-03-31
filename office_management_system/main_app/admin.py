from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
# Register your models here.


class UserModel(UserAdmin):
    ordering = ('email',)


admin.site.register(CustomUser, UserModel)
admin.site.register(Manager)
admin.site.register(Employer)
admin.site.register(Department)
admin.site.register(TodoList)
admin.site.register(Meeting)
admin.site.register(Project)
