from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from app.views import MovieListAPIView, MovieDetailAPIView, MovieByTypeListAPIView, MovieByGenreListAPIView, \
    NotificationListAPIView, UserBalanceListAPIView, UserFillBalanceAPIView, \
    TelegramIDUpdateView, CheckTelegramUserAPIView, FillBalanceWithTelegramAPIView, \
    SendOTPGenericAPIView, VerifyOTPAndRegisterGenericAPIView, UserLoginGenericAPIView, \
    UserMessageModelViewSet, AdminMessageModelViewSet, PurchaseSubscriptionCreateAPIView, \
    PurchaseCreateAPIView, NewsModelViewSet, \
    MovieMostWatchedListAPIView, RandomMovieListAPIView, PremierMovies, FavouritesMovieModelViewSet, \
    MovieMostLikedListAPIView, MovieByCountriesListAPIView, MovieNewsListAPIView, \
    MovieCommentsModelViewSet, UserLastSearchListView, MostCommentedMoviesListAPIView, \
    SubscribersModelViewSet, PurchaseDeleteAPIView, \
    PurchaseSubscriptionDeleteAPIView, PaymentSubscriptionCreateAPIView, PaymentPurchasedMovieCreateAPIView, \
    UserCheckBalanceWithTelegramRetrieveAPIView, CreateOrderForMovieListCreateAPIView, \
    CreateOrderForSubscriptionCreateAPIView, NotificationDestroyAPIView, \
    TranslateMoviesListAPIView, PaymentTranslateMoviesListCreateAPIView, TopDonatersListAPIView, LastDonatesListAPIView

router = DefaultRouter()

# Chat
router.register('message-to-admin', UserMessageModelViewSet, basename='chat-admin')
router.register('message-to-user', AdminMessageModelViewSet, basename='chat-user')

# News
router.register('news', NewsModelViewSet, basename='news')

# Favourite Movie
router.register('favourite-movies', FavouritesMovieModelViewSet, basename='favourite-movies')

# Comments
router.register('comments', MovieCommentsModelViewSet, basename='comment')

# Subscribers
router.register('subscribers', SubscribersModelViewSet, basename='subscribers')


urlpatterns = [
    path('router/', include(router.urls)),
    path('get-token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('get-token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    #Auth
    path('sign-up/', SendOTPGenericAPIView.as_view(), name='UserRegister'),
    path('login/', UserLoginGenericAPIView.as_view(), name='UserLogin'),
    path('verify-code/', VerifyOTPAndRegisterGenericAPIView.as_view(), name='verify'),

    # Movies
    path('genre/<str:genre>/', MovieByGenreListAPIView.as_view(), name='movie-by-type'),
    path('category/<str:category>/', MovieByTypeListAPIView.as_view(), name='movie-by-category'),
    path('movie-country/<str:country>/', MovieByCountriesListAPIView.as_view(), name='movie-by-country'),
    path('movies/', MovieListAPIView.as_view(), name='movie-list'),
    path('movie/<slug:slug>/', MovieDetailAPIView.as_view(), name='movie-detail'),
    path('movie-most-watched/', MovieMostWatchedListAPIView.as_view(), name='movie-most-watched'),
    path('movie-random/', RandomMovieListAPIView.as_view(), name='movie-random'),
    path('movie-most-liked/', MovieMostLikedListAPIView.as_view(), name='movie-most-liked'),
    path('premier-movies/', PremierMovies.as_view(), name='premier-movies'),
    path('movies-translate/', TranslateMoviesListAPIView.as_view(), name='movies-translate'),
    path('movie-news/', MovieNewsListAPIView.as_view(), name='movie-news'),
    path('most-commented/', MostCommentedMoviesListAPIView.as_view(), name='most-commented'),
    path('last-search/', UserLastSearchListView.as_view(), name='last-search'),

    # Notifications
    path('notifications/', NotificationListAPIView.as_view(), name='notification-list'),
    path('notifications-delete/<int:pk>/', NotificationDestroyAPIView.as_view(), name='notification-destroy'),

    # Purchases(Orders)
    # Purchase Subscriptions
    path('create-order-subscription/', CreateOrderForSubscriptionCreateAPIView.as_view(), name='create-order'),
    path('order-subscription-create/', PurchaseSubscriptionCreateAPIView.as_view(), name='order-subscription'),
    path('order-subscription-delete/<int:pk>/', PurchaseSubscriptionDeleteAPIView.as_view(), name='order-subscription-delete'),
    path('order-subcription-payment/', PaymentSubscriptionCreateAPIView.as_view(), name='order-subcription-payment'),

    #Purchase Movies
    path('create-order-movie/', CreateOrderForMovieListCreateAPIView.as_view(), name='create-order'),
    path('purchase-movie-create/', PurchaseCreateAPIView.as_view(), name='movie-purchase'),
    path('purchase-movie-delete/<int:pk>/', PurchaseDeleteAPIView.as_view(), name='purchase-movie-delete'),
    path('purchased-movie-payment/', PaymentPurchasedMovieCreateAPIView.as_view(), name='purchased-movie-payment'),


    # Telegram
    path('user-check-balance/', UserBalanceListAPIView.as_view(), name='user-balance-list'),
    path('user-fill-balance/', UserFillBalanceAPIView.as_view(), name='user-balance-fill'),
    path('user-update/', TelegramIDUpdateView.as_view(), name='user-update'),
    path('telegram-user-id/', CheckTelegramUserAPIView.as_view(), name='tel-user'),
    path('user-fill-balance-telegram/', FillBalanceWithTelegramAPIView.as_view(), name='balance-fill-tel'),
    path('check-balance-telegram/<int:telegram_id>/', UserCheckBalanceWithTelegramRetrieveAPIView.as_view(), name='check-balance-tel'),
    path('translate-movie-payment/', PaymentTranslateMoviesListCreateAPIView.as_view(), name='translate-movie-payment'),
    path('top-donaters/', TopDonatersListAPIView.as_view(), name='top-donaters'),
    path('last-donates/', LastDonatesListAPIView.as_view(), name='last-donates'),

]
