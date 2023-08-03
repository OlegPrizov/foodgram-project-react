from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
        'recipes_count',
        'followers_count'
    )
    list_filter = ('email', 'username',)

    @admin.display(description='Кол-во рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Кол-во подписчиков')
    def followers_count(self, obj):
        return obj.following.count()


admin.site.unregister(Group)
