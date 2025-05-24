
from celery import shared_task
from django.core.mail import send_mail, get_connection

from .models import PurchaseMovie, Notification, OrderSubscription, Subscribers, OrderSubscriptionItem


def create_notification(user, message, payment_method):

    Notification.objects.create(user=user,
                                message=message,
                                notification_type=payment_method)



@shared_task
def send_purchase_created_notification(order_id):
    try:
        instance = PurchaseMovie.objects.get(pk=order_id)
        create_notification(instance.purchase.user, f"You order of {instance.movie.title} is pending...", "PURCHASE")
    except PurchaseMovie.DoesNotExist:
        pass




@shared_task
def send_purchase_accepted_notification(order_id):
    try:
        instance = PurchaseMovie.objects.get(pk=order_id)
        create_notification(instance.purchase.user, f"You order of {instance.movie.title} is accepted!", "PURCHASE")
    except PurchaseMovie.DoesNotExist:
        pass


@shared_task
def send_purchase_subscription_notification(order_id):
    try:
        instance = OrderSubscriptionItem.objects.get(pk=order_id)
        create_notification(instance.order.user, f"You order Subscription of {instance.subscription.subscribe.name} is pending...!", "PURCHASE")
    except PurchaseMovie.DoesNotExist:
        pass


@shared_task
def send_purchase_subscription_accepted_notification(order_id):
    try:
        instance = OrderSubscriptionItem.objects.get(pk=order_id)
        create_notification(instance.order.user, f"You order Subscription of {instance.subscription.subscribe.name} is accepted!", "PURCHASE")
    except PurchaseMovie.DoesNotExist:
        pass





# @shared_task
# def send_subscription_notification(order_id, subscription_id):
#     try:
#         instance = OrderSubscriptionItem.objects.select_related('order__user', 'subscription').get(order=order_id, subscription=subscription_id)
#         create_notification(instance, "Your subscription for '{title}' is pending approval.")
#     except OrderSubscriptionItem.DoesNotExist:
#         pass



# @shared_task
# def send_subscription_accepted_notification(order_id):
#     try:
#         instance = OrderSubscriptionItem.objects.get(order=order_id)
#         create_notification(instance, "Your subscription for '{title}' has been accepted.")
#     except OrderSubscription.DoesNotExist:
#         pass



@shared_task
def send_otp_email(email, code):
    print('123')
    subject = "Your Verification Code"
    message = f"Your verification code is: {code}"
    from_email = 'vnoreply58@gmail.com'
    recipient_list = [email]

    return send_mail(subject, message, from_email, recipient_list)



