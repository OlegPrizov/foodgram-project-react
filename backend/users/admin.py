from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'password'
    )
    list_filter = ('email', 'username',)
    list_editable = ('password',)


admin.site.register(User, UserAdmin)
