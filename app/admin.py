from django.contrib import admin
from django.contrib.admin import register, ModelAdmin, StackedInline
import nested_admin
from app.models.movie import *
from app.models.orders import Purchase, PurchaseMovie, Notification, Payment, OrderSubscription, PaymentTranslateMovie, PaymentSubscription
from app.models.users import User, UserDevice

admin.site.register(
    [Countries, Language, MovieComment, Genre, Category, Chat, Message, AdminAnswer, Season, UserDevice,
     News, FavouriteMovies, OrderSubscription, TranslateMovies, PaymentTranslateMovie, PaymentSubscription])


@register(User)
class User(ModelAdmin):
    list_display = ('username', 'email', 'telegram_id', 'balance', 'is_active', 'subscription')
    list_editable = ('is_active', 'subscription',)


@register(Purchase)
class Purchase(ModelAdmin):
    list_display = ('user', 'created_at')


@register(PurchaseMovie)
class PurchaseMovie(ModelAdmin):
    list_display = ('purchase', 'movie', 'status', 'created_at')

    list_editable = ('status',)


@register(CastMembers)
class CastMember(ModelAdmin):
    pass


@register(Payment)
class Payment(ModelAdmin):
    list_display = ('purchase_movie', 'status', 'payment_method')
    list_editable = ('payment_method', 'status',)


@register(Subscriptions)
class Subscriptions(ModelAdmin):
    list_display = ('name', 'description', 'available_movies', 'is_active')
    list_editable = ('is_active', 'available_movies',)


@register(Subscribers)
class SubscribersList(ModelAdmin):
    list_display = ('user', 'subscribe_item', 'valid_at', 'expires_at', 'is_active')
    list_editable = ('is_active',)

    def expires_at(self, obj):
        return obj.expires_at


@register(SubscriptionItems)
class SubscriptionsItems(ModelAdmin):
    list_display = ('subscribe', 'valid_until_days', 'price')
    list_editable = ('price', 'valid_until_days',)


@register(Notification)
class Notification(ModelAdmin):
    list_display = ('id', 'user', 'message', 'notification_type', 'created_at')


# @register(OrderSubscription)
# class OrderSubscription(ModelAdmin):
#     list_display = ('id', 'user', 'subscription', 'status')
#     list_editable = ('status', 'subscription',)


class EpisodeInline(nested_admin.NestedStackedInline):
    model = Episode
    extra = 1

class SeasonInline(nested_admin.NestedStackedInline):
    model = Season
    inlines = [EpisodeInline]
    extra = 1


@admin.register(Movie)
class MovieAdmin(nested_admin.NestedModelAdmin):
    def get_inline_instances(self, request, obj=None):
        inlines = []

        if obj and obj.category.name.lower() == 'serial':
            inlines = [SeasonInline(self.model, self.admin_site)]

        return inlines
