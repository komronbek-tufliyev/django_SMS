from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

# Create your models here.


class User(AbstractUser):
    _USER_ERROR_MESSAGE = 'Bunday foydalanuvchi topilmadi'

    username = None
    full_name = models.CharField(max_length=150, null=True, blank=True)
    phone_regex = RegexValidator(regex=r'^998[0-9]{2}[0-9]{7}$', message='Faqat o\'zbek raqamlari tasdiqlanadi')
    phone = models.CharField(_('Telefon raqami'), validators=[phone_regex], max_length=17, unique=True)
    eskiz_id = models.CharField(max_length=20, null=True, blank=True)
    key = models.CharField(max_length=100, null=True, blank=True)
    eskiz_code = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)

    USERNAME_FIELD: str = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def isVerified(self):
        return self.is_verified

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-id']
        permissions = [
            
        ]
    

class SMSClient(models.Model):
    AUTH_TOKEN_LEN = 10000

    token = models.CharField(max_length=10000, blank=False, null=True)

class SMSToken(models.Model):
    name = models.CharField(max_length=150)
    token = models.CharField(max_length=150)
    create_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'SMS Token'
        verbose_name_plural = 'SMS Tokens'
        ordering = ['-id']

class SMSLog(models.Model):
    phone = models.CharField(max_length=17)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    message = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'SMS Log'
        verbose_name_plural = 'SMS Logs'
        ordering = ['-id']
