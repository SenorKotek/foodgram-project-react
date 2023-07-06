from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin
from users.models import FoodgramUser


@register(FoodgramUser)
class FoodgramUserAdmin(UserAdmin):
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
