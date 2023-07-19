from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User, Subscriptions


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        "is_active",
        "username",
        "first_name",
        "last_name",
        "email",
    )
    search_fields = (
        "username",
        "email",
    )
    list_filter = (
        "is_active",
        "first_name",
        "email",
    )
    save_on_top = True


@admin.register(Subscriptions)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
