
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from app.models import PurchaseMovie, Payment, SubscriptionItems, Subscribers, TranslateMovies, OrderSubscriptionItem, PaymentSubscription
from app.task import send_purchase_created_notification, send_purchase_accepted_notification, send_purchase_subscription_notification, \
    send_purchase_subscription_accepted_notification



@receiver(post_save, sender=PurchaseMovie)
def handle_purchase_notifications(sender, instance, created, **kwargs):
    if created and instance.status == "PENDING":
        send_purchase_created_notification.delay(instance.id)

    elif instance.status == "ACCEPTED":
        send_purchase_accepted_notification.delay(instance.id)


@receiver(post_save, sender=OrderSubscriptionItem)
def handle_subscription_notifications(sender, instance, created, **kwargs):
    if created and instance.status == "PENDING":
        send_purchase_subscription_notification.delay(instance.id)

    elif instance.status == "COMPLETED":
        send_purchase_subscription_accepted_notification.delay(instance.id)


# @receiver(post_save, sender=OrderSubscriptionItem)
# def handle_subscription_notifications(sender, instance, created, **kwargs):
#     if created and instance.status == "PENDING":
#         send_subscription_notification.delay(instance.order.id, instance.subscription)
    #
    # elif instance.status == "ACCEPTED":
    #     send_purchase_accepted_notification.delay(instance.order.id, instance.subscription)


@receiver(post_save, sender=Payment)
def change_status_purchase_after_payment(sender, instance, **kwargs):
    purchase_movie = instance.purchase_movie

    if instance.status == "COMPLETED" and purchase_movie.status == "PENDING":
        purchase_movie.status = "ACCEPTED"
        purchase_movie.save(update_fields=["status"])


@receiver(post_save, sender=PaymentSubscription)
def change_status_subscription_after_payment(sender, instance, **kwargs):
    order = instance.order

    if instance.status == "COMPLETED" and order.status == "PENDING":
        order.status = "COMPLETED"
        order.save(update_fields=["status"])



@receiver(pre_save, sender=SubscriptionItems)
def update_subscription_status(sender, instance, **kwargs):
    if instance.valid_until_days == 0:
        Subscribers.objects.filter(subscribe_item=instance).update(is_active=False)




