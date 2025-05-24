from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from app.models.base import TimeModelBase


from django.db.models import CharField, BooleanField, ForeignKey, ImageField, PositiveIntegerField, \
    CASCADE, TextChoices, Model, OneToOneField, DateTimeField, TextField, GenericIPAddressField, PositiveBigIntegerField

from app.manager import CustomUserManager


class User(AbstractUser):

    class UserSubsription(TextChoices):
        LITE = 'LITE', 'lite'
        PRO = 'PRO', 'pro'
        PREMIUM = 'PREMIUM', 'premium'

    address = CharField(max_length=255, blank=True, null=True, verbose_name=_("address"))
    telegram_id = CharField(max_length=30, blank=True, null=True, unique=True, validators=[
        RegexValidator(regex=r'^\d+$', message="Telegram ID must contain only numbers.")],
                            verbose_name=_("telegram id"))

    phone = CharField(max_length=11, unique=True, blank=True, null=True, verbose_name=_("phone"))
    image = ImageField(upload_to='user/%Y/%m/%d/', default='default.jpg', blank=True, verbose_name=_("image"))
    balance = PositiveBigIntegerField(db_default=0, verbose_name=_('user balance'))

    subscription = CharField(max_length=25, choices=UserSubsription, verbose_name=_("subscription"), null=True, blank=True)


    objects = CustomUserManager()

    def __str__(self):
        return f'{self.username} {self.email}'







class UserDevice(TimeModelBase):
    user = ForeignKey(User, on_delete=CASCADE, verbose_name=_("user"))
    device_id = CharField(max_length=255, verbose_name=_("device"))
    user_agent = TextField()
    ip_address = GenericIPAddressField()
    last_login = DateTimeField(auto_now_add=True, verbose_name=_("last login"))

    def __str__(self):
        return f'{self.user.username}, Device: {self.device_id}, Last Login: {self.last_login}'

