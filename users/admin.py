from django.contrib import admin
from .models import (
    User,
    SMSLog, 
    SMSToken,
    SMSClient,
)
# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'phone',
        'id',
        'full_name',
        'is_verified',
        'is_deleted',
        'is_staff',
        'is_superuser',
        'date_joined',
        'last_login',
    )
    list_filter = (
        'is_verified',
        'is_deleted',
        'is_staff',
        'is_superuser',
    )
    search_fields = (
        'full_name',
        'phone',
    )
    ordering = (
        '-id',
    )
    list_per_page = 20
    readonly_fields = (
        'date_joined',
        'last_login',
    )
    fieldsets = (
        (
            'Asosiy ma\'lumotlar',
            {
                'fields': (
                    'full_name',
                    'phone',
                    'password',
                ),
            },
        ),
        (
            'Qo\'shimcha ma\'lumotlar',
            {
                'fields': (
                    'eskiz_id',
                    'key',
                    'eskiz_code',
                    'is_verified',
                    'is_deleted',
                    'date_joined',
                    'last_login',
                ),
            },
        ),
        (
            'Tizim ma\'lumotlari',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
    )
    add_fieldsets = (
        (
            'Asosiy ma\'lumotlar',
            {
                'fields': (
                    'full_name',
                    'phone',
                    'password1',
                    'password2',
                ),
            },
        ),
        (
            'Qo\'shimcha ma\'lumotlar',
            {
                'fields': (
                    'eskiz_id',
                    'key',
                    'eskiz_code',
                    'is_verified',
                    'is_deleted',
                ),
            },
        ),
        (
            'Tizim ma\'lumotlari',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
    )

@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = (
        'phone',
        'owner',
        'message',
        'create_at',
    )
    list_filter = (
        'owner',
    )
    search_fields = (
        'phone',
        'owner__full_name',
        'owner__phone',
    )
    ordering = (
        '-id',
    )
    list_per_page = 20
    readonly_fields = (
        'create_at',
    )
    fieldsets = (
        (
            'Asosiy ma\'lumotlar',
            {
                'fields': (
                    'phone',
                    'owner',
                    'message',
                    'create_at',
                ),
            },
        ),
    )

@admin.register(SMSToken)
class SMSTokenAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'token',
        'create_at',
    )
    search_fields = (
        'name',
    )
    ordering = (
        '-id',
    )
    list_per_page = 20
    readonly_fields = (
        'create_at',
    )
    fieldsets = (
        (
            'Asosiy ma\'lumotlar',
            {
                'fields': (
                    'name',
                    'token',
                    'create_at',
                ),
            },
        ),
    )


@admin.register(SMSClient)
class SMSClientAdmin(admin.ModelAdmin):
    list_display = ['token']

