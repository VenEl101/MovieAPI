
from django.db.models import Model, CharField, TextField, ForeignKey, DateField, DateTimeField, FileField, ImageField, \
    CASCADE, URLField, ManyToManyField, BooleanField, DecimalField, TextChoices, PositiveIntegerField

from app.models.users import User
from app.models.base import TimeModelBase
from app.models.movie import SubscriptionItems, TranslateMovies


class Purchase(TimeModelBase):
    user = ForeignKey('User', related_name='orders', on_delete=CASCADE)

    def __str__(self):
        return self.user.username


class PurchaseMovie(TimeModelBase):

    class STATUS(TextChoices):
        PENDING = 'PENDING', 'pending'
        ACCEPTED = 'ACCEPTED', 'accepted'

    purchase = ForeignKey('Purchase', related_name='movies', on_delete=CASCADE)
    movie = ForeignKey('Movie', related_name='movies', on_delete=CASCADE)
    status = CharField(max_length=25, choices=STATUS.choices, db_default=STATUS.PENDING)

    @property
    def get_price(self):
        return self.movie.price

    def __str__(self):
        return f'Order #{self.purchase.id} Movie: {self.movie.title}'



class Payment(TimeModelBase):

    class PaymentMethod(TextChoices):

        BALANCE = 'BALANCE', 'balance'
        PAYME = 'PAYME', 'payme'

    class STATUS(TextChoices):
        PENDING = 'PENDING', 'pending'
        FAILED = 'FAILED', 'failed'
        COMPLETED = 'COMPLETED', 'completed'

    purchase_movie = ForeignKey('PurchaseMovie', related_name='payments', on_delete=CASCADE)
    status = CharField(max_length=10, choices=STATUS, db_default=STATUS.PENDING)
    payment_method = CharField(max_length=25, choices=PaymentMethod, null=True, blank=True, db_default=PaymentMethod.PAYME)


    @property
    def price(self):
        return self.purchase_movie.get_price

    def __str__(self):
        return f'Order #{self.purchase_movie.movie.title} Payment: {self.payment_method}'




class Notification(TimeModelBase):

    class Type(TextChoices):
        PURCHASE = 'PURCHASE', 'purchase'


    user = ForeignKey('User', related_name='notifications', on_delete=CASCADE)
    message = CharField(max_length=100)
    notification_type = CharField(max_length=20, choices=Type.choices, db_default=Type.PURCHASE)

    def __str__(self):
        return self.message

    class Meta:
        ordering = ['-created_at']




class OrderSubscription(TimeModelBase):

    user = ForeignKey('User', related_name='subscriptions', on_delete=CASCADE)

    def __str__(self):
        return f"order #{self.id}"



class OrderSubscriptionItem(TimeModelBase):

    class Status(TextChoices):
        PENDING = 'PENDING', 'pending'
        FAILED = 'FAILED', 'failed'
        COMPLETED = 'COMPLETED', 'completed'

    order = ForeignKey('OrderSubscription', related_name='items', on_delete=CASCADE)
    subscription = ForeignKey('SubscriptionItems', related_name='status', on_delete=CASCADE)
    status = CharField(max_length=25, choices=Status.choices, db_default=Status.PENDING)

    @property
    def get_price(self):
        return self.subscription.price

    def __str__(self):
        return f'Order #{self.id} Status: {self.status}'



class PaymentSubscription(TimeModelBase):

    class PaymentMethod(TextChoices):
        BALANCE = 'BALANCE', 'Balance'
        PAYME = 'PAYME', 'payme'

    class Status(TextChoices):
        PENDING = 'PENDING', 'pending'
        FAILED = 'FAILED', 'failed'
        COMPLETED = 'COMPLETED', 'completed'

    order = ForeignKey("OrderSubscriptionItem", related_name='payments', on_delete=CASCADE)
    status = CharField(max_length=25, choices=Status.choices, db_default=Status.PENDING)
    payment_method = CharField(max_length=30, choices=PaymentMethod.choices, db_default=PaymentMethod.BALANCE)

    @property
    def price(self):
        return self.order.get_price

    def __str__(self):
        return f"{self.order}"




class PaymentTranslateMovie(TimeModelBase):

    user = ForeignKey('User', related_name='translated_movies', on_delete=CASCADE)
    translate_movie = ForeignKey('TranslateMovies', on_delete=CASCADE)
    amount = PositiveIntegerField()

    def __str__(self):
        return f'Translate Movie #{self.translate_movie.id}'


