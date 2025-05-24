from django.contrib.auth.hashers import make_password
from django.contrib.postgres.search import TrigramSimilarity
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from redis.commands.search import Search
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView, UpdateAPIView, GenericAPIView, DestroyAPIView, ListCreateAPIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from app.models.base import NonePaginationListAPIView
from app.models.movie import Movie, Subscribers, Message, \
    AdminAnswer, News, FavouriteMovies, MovieComment, Chat, LastSearch, TranslateMovies

from app.models.orders import Purchase, PurchaseMovie, Notification, OrderSubscription, Payment, PaymentSubscription, \
    OrderSubscriptionItem, PaymentTranslateMovie

from app.models.users import User, UserDevice
from app.serializer import MovieModelSerializer, MovieDetailModelSerializer, PurchaseModelSerializer, \
    PurchaseMovieModelSerializer, NotificationModelSerializer, UserBalanceModelSerializer, \
    UserFillBalanceModelSerializer, PaymentModelSerializer, SubscribersModelSerializer, \
    TelegramIDUpdateSerializer, UserFillBalanceWithTelegramModelSerializer, \
    UserCheckBalanceModelSerializer, OTPVerifySerializer, PreRegisterSerializer, UserLoginSerializer, \
    NewsModelSerializer, FavouritesMoviesModelSerializer, \
    CommentModelSerializer, UserMessageSerializer, AdminMessageSerializer, \
    UserSearchModelSerializer, UpdateTranslateMovieStatusModelSerializer, PaymentMovieModelSerializer, \
    PaymentSubscriptionModelSerializer, CreateOrderForMovieModelSerializer, OrderSubscriptionModelSerializer, \
    OrderSubscriptionItemModelSerializer, TranslateMovieModelSerializer, PaymentTranslateMovieModelSerializer, \
    TopDonaterModelSerializer, LastDonatesModelSerializer

from app.task import send_otp_email
from app.utils import gen_ran_num, generate_device_id


@extend_schema(tags=['auth'])
class SendOTPGenericAPIView(GenericAPIView):
    serializer_class = PreRegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')


        code = gen_ran_num()

        cache.set(f'code_{email}', {'code': code, 'username': username, 'email': email, 'password': password},
                  timeout=120)
        send_otp_email.delay(email, code)


        return Response({'message': 'VerificationCode sent to email.'}, status=status.HTTP_200_OK)





@extend_schema(tags=['auth'])
class VerifyOTPAndRegisterGenericAPIView(GenericAPIView):
    serializer_class = OTPVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        code = int(serializer.validated_data.get('code'))

        cached_data = cache.get(f'code_{email}')

        if not cached_data:
            return Response({'error': 'VerificationCode expired or not found.'}, status=400)

        if code != cached_data['code']:
            return Response({'error': f'Invalid code!'}, status=400)

        email = cached_data.get('email')
        username = cached_data.get('username')
        password = cached_data.get('password')
        print(email, username, password, type(password))


        if User.objects.filter(email=email).exists():
            return Response({'error': 'This Email already exist.'}, status=400)

        User.objects.create_user(email=email, username=username, password=password)

        cache.delete(f'code_{email}')

        return Response({'message': 'User registered successfully!'}, status=201)


@extend_schema(tags=['auth'])
class UserLoginGenericAPIView(GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get('user')
        device_id = generate_device_id(request)
        device_count = UserDevice.objects.filter(user=user).count()

        if not device_count <= 2:
            return Response({'error': 'Only 2 devices allowed!.'}, status=403)

        UserDevice.objects.get_or_create(
            user=user,
            device_id=device_id,
            defaults={
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': request.META.get('REMOTE_ADDR', '')
            }
        )

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        }, status=status.HTTP_200_OK)


@extend_schema(tags=['movie'])
class PremierMovies(ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieModelSerializer
    pagination_class = PageNumberPagination

    # pagination_class.page_size = 10

    def get_queryset(self):
        return super().get_queryset().filter(is_premier=True)


@extend_schema(tags=['movie'])
class MovieByCountriesListAPIView(ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieModelSerializer

    pagination_class = PageNumberPagination

    def get_queryset(self):
        country = self.kwargs.get('country')
        return super().get_queryset().filter(country__name=country)


class MovieCommentsModelViewSet(ModelViewSet):
    queryset = MovieComment.objects.all()
    serializer_class = CommentModelSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(tags=['movie'])
class MostCommentedMoviesListAPIView(NonePaginationListAPIView):

    queryset = Movie.objects.annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments')
    serializer_class = MovieModelSerializer
    permission_classes = [AllowAny]


@extend_schema(tags=['movie'])
class MovieMostWatchedListAPIView(ListAPIView):
    queryset = Movie.objects.order_by('-views')
    serializer_class = MovieModelSerializer


@extend_schema(tags=['movie'])
class MovieMostLikedListAPIView(ListAPIView):
    queryset = Movie.objects.order_by('-rate')
    serializer_class = MovieModelSerializer


@extend_schema(tags=['movie'])
class RandomMovieListAPIView(ListAPIView):
    serializer_class = MovieModelSerializer

    def get_queryset(self):
        return Movie.objects.order_by('?')[:5]


@extend_schema(tags=['movie'])
class MovieByTypeListAPIView(ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieModelSerializer

    def get_queryset(self):
        category = self.kwargs.get('category', '')
        return super().get_queryset().filter(category__name__icontains=category)


@extend_schema(tags=['movie'])
class MovieByGenreListAPIView(ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieModelSerializer


    def get_queryset(self):
        genre_name = self.kwargs.get('genre', '')
        return super().get_queryset().filter(genre__name__icontains=genre_name)


@extend_schema(tags=['movie'])
class MovieListAPIView(ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieModelSerializer
    pagination_class = None
    filter_backends = [SearchFilter]

    def get_queryset(self):
        queryset = Movie.objects.all()
        query = self.request.query_params.get('search')
        if query is not None:
            queryset = queryset.annotate(
                similarity=TrigramSimilarity('title', query)
            ).filter(similarity__gte=0.2).order_by('-similarity')


            if self.request.user.is_authenticated:
                LastSearch.objects.create(
                    user=self.request.user,
                    search=query.strip(),
                )

        return queryset


@extend_schema(tags=['movie'])
class MovieDetailAPIView(RetrieveAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieDetailModelSerializer
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        movie = self.get_object()
        data = self.get_serializer(movie).data

        with transaction.atomic():
            movie.views += 1
            movie.save(update_fields=['views'])

        if self.has_video_access(user, movie) is False:
            data.pop('video', None)

        return Response(data)

    def has_video_access(self, user, movie):

        if movie.access_type == 'PURCHASE':
            return self.has_purchased(user, movie)

        elif movie.access_type == 'FREE':
            return True

        if movie.subscribe == 'Lite' and movie.access_type == 'SUBSCRIPTION':
            return user.subscription in ['LITE', 'PRO', 'PREMIUM']

        elif movie.subscribe == 'Pro' and movie.access_type == 'SUBSCRIPTION':
            return user.subscription in ['PRO', 'PREMIUM']
        elif movie.subscribe == 'Premium' and movie.access_type == 'SUBSCRIPTION':
            return user.subscription == 'PREMIUM'

        return False

    def has_purchased(self, user, movie):
        return PurchaseMovie.objects.filter(
            purchase__user=user,
            movie=movie,
            status='ACCEPTED'
        ).exists()



@extend_schema(tags=['movie'])
class MovieNewsListAPIView(ListAPIView):
    queryset = News.objects.all()
    serializer_class = NewsModelSerializer


@extend_schema(tags=['movie'])
class FavouritesMovieModelViewSet(ModelViewSet):
    queryset = FavouriteMovies.objects.all()
    serializer_class = FavouritesMoviesModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


@extend_schema(tags=['Subscribes'])
class SubscribersModelViewSet(ModelViewSet):
    queryset = Subscribers.objects.all()
    serializer_class = SubscribersModelSerializer
    permission_classes = [IsAdminUser]




@extend_schema(tags=['Create-Order'])
class CreateOrderForMovieListCreateAPIView(ListCreateAPIView):
    queryset = Purchase.objects.all()
    serializer_class = CreateOrderForMovieModelSerializer
    permission_classes = [IsAuthenticated,]

    # def get_queryset(self):
    #     return super().get_queryset().filter(purchase__user=self.request.user)

    def create(self, request, *args, **kwargs):
        if Purchase.objects.filter(user=request.user).exists():
            return Response({'message': 'User already has an order!'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



@extend_schema(tags=['Purchase'])
class PurchaseCreateAPIView(ListCreateAPIView):
    queryset = PurchaseMovie.objects.all()
    serializer_class = PurchaseMovieModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        purchase = serializer.validated_data['purchase']
        movie = serializer.validated_data['movie']

        if PurchaseMovie.objects.filter(purchase=purchase, movie=movie).exists():
            return Response({'message': 'Order already exists!'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()


        return Response({'message': 'Successfully created purchase'}, status=status.HTTP_201_CREATED)



@extend_schema(tags=['PurchaseDelete'])
class PurchaseDeleteAPIView(DestroyAPIView):
    queryset = PurchaseMovie.objects.all()
    serializer_class = PurchaseMovieModelSerializer
    lookup_field = 'pk'

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Purchase deleted successfully'}, status=status.HTTP_204_NO_CONTENT)




@extend_schema(tags=['Purchases-List-View'])
class CreatePurchaseSubscriptionListAPIView(NonePaginationListAPIView):
    queryset = OrderSubscription.objects.all()
    serializer_class = OrderSubscriptionItemModelSerializer

    def get_queryset(self):
        return super().get_queryset().filter(order__user=self.request.user)




@extend_schema(tags=['Create-Order'])
class CreateOrderForSubscriptionCreateAPIView(ListCreateAPIView):
    queryset = OrderSubscription.objects.all()
    serializer_class = OrderSubscriptionModelSerializer
    permission_classes = [IsAuthenticated,]

    def create(self, request, *args, **kwargs):
        if OrderSubscription.objects.filter(user=request.user).exists():
            return Response({'message': 'User already has an order!'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=['Purchase'])
class PurchaseSubscriptionCreateAPIView(ListCreateAPIView):
    queryset = OrderSubscriptionItem.objects.all()
    serializer_class = OrderSubscriptionItemModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pk = serializer.validated_data.get('order')
        order = get_object_or_404(OrderSubscription, pk=pk.id)

        subscription = serializer.validated_data.get('subscription')

        if OrderSubscriptionItem.objects.filter(order=order, subscription=subscription).exists():
            return Response({'message': 'Order already exists!'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response({'message': 'Successfully created subscription'}, status=status.HTTP_201_CREATED)


@extend_schema(tags=['PurchaseDelete'])
class PurchaseSubscriptionDeleteAPIView(DestroyAPIView):
    queryset = OrderSubscriptionItem.objects.all()
    serializer_class = OrderSubscriptionItemModelSerializer
    lookup_field = 'pk'

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Subscription deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Payment'])
class PaymentSubscriptionCreateAPIView(CreateAPIView):
    serializer_class = PaymentSubscriptionModelSerializer

    def create(self, request, *args, **kwargs):
        user = request.user

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pk = serializer.validated_data.get('order')
        order = get_object_or_404(OrderSubscriptionItem, id=pk.id)
        payment_method = serializer.validated_data.get('payment_method')

        if PaymentSubscription.objects.filter(order=order, status='COMPLETED').exists():
            return Response({'message': 'You already have this Subscription!'}, status=status.HTTP_400_BAD_REQUEST)

        if payment_method == 'BALANCE' and order.status == 'PENDING':
            if user.balance < 0 and user.balance < order.get_price:
                return Response({'message': 'Not enough funds!'}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                user.balance -= order.get_price
                print(user.balance)
                user.save()
                order.status = "COMPLETED"
                order.save()
                serializer.save(order=order, status='COMPLETED')
                return Response({'message': 'Payment succeeded!'}, status=status.HTTP_200_OK)


        serializer.save()
        return Response({'message': 'Successfully created subscription'}, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Payment'])
class PaymentPurchasedMovieCreateAPIView(CreateAPIView):
    serializer_class = PaymentModelSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pk = serializer.validated_data.get('purchase_movie')
        payment_method = serializer.validated_data.get('payment_method')
        purchase_movie = get_object_or_404(PurchaseMovie, pk=pk.id)
        price = purchase_movie.movie.price


        if payment_method == 'BALANCE':
            if user.balance >= 0 and user.balance >= price:
                user.balance -= price
                user.save()
                purchase_movie.status = 'ACCEPTED'
                purchase_movie.save()

                serializer.save(purchase_movie=purchase_movie)
                return Response({'message': 'Payment successfully created!'}, status=status.HTTP_201_CREATED)

            return Response({'message': 'Not enough money!'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response({'message': 'Payment Successfully created!'}, status=status.HTTP_201_CREATED)


@extend_schema(tags=['notification'])
class NotificationListAPIView(NonePaginationListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationModelSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


@extend_schema(tags=['notification'])
class NotificationDestroyAPIView(DestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationModelSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'pk'

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Subscription deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['payment'])
class PaymentMovieListAPIView(ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentMovieModelSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)



@extend_schema(tags=['balance'])
class UserBalanceListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserBalanceModelSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return super().get_queryset().filter(email=self.request.user.email)


@extend_schema(tags=['balance'])
class UserCheckBalanceWithTelegramRetrieveAPIView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserCheckBalanceModelSerializer
    lookup_field = 'telegram_id'


@extend_schema(tags=['balance'])
class UserFillBalanceAPIView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserFillBalanceModelSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data['amount']

        with transaction.atomic():
            instance.balance += amount
            instance.save()

            Notification.objects.create(
                user=self.request.user,
                message=f"Your balance filled by {amount}!",
                notification_type='BALANCE_ADD'
            )

        return Response({'status': 'success',
                         'Added amount': amount,
                         'current_balance': instance.balance, }, status=status.HTTP_200_OK)


@extend_schema(tags=['telegram'])
class FillBalanceWithTelegramAPIView(GenericAPIView):

    def post(self, request):
        serializer = UserFillBalanceWithTelegramModelSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        telegram_id = request.data.get('telegram_id')
        amount = request.data.get('amount')

        with transaction.atomic():

            try:
                user = User.objects.select_for_update().get(telegram_id=telegram_id)
            except User.DoesNotExist:
                return Response({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

            user.balance += amount
            user.save()

            Notification.objects.create(
                user=user,
                message=f"Your balance was filled by {amount}!",
                notification_type='BALANCE_ADD'
            )

            return Response({'status': 'success', }, status=status.HTTP_200_OK)


@extend_schema(tags=['telegram'])
class CheckTelegramUserAPIView(GenericAPIView):

    def get(self, request, *args, **kwargs):
        telegram_id = request.query_params.get('telegram_id', None)

        if not telegram_id:
            return Response(
                {"error": "Telegram ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_exists = User.objects.filter(telegram_id=telegram_id).exists()

        return Response(
            {"exists": user_exists},
            status=status.HTTP_200_OK
        )


@extend_schema(tags=['telegram'])
class TelegramIDUpdateView(UpdateAPIView):
    serializer_class = TelegramIDUpdateSerializer
    queryset = User.objects.all()
    http_method_names = ['patch']

    def get_object(self):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data['user']

    def perform_update(self, serializer):
        user = serializer.validated_data['user']
        user.telegram_id = serializer.validated_data['telegram_id']
        user.save(update_fields=['telegram_id'])

    def patch(self, request, *args, **kwargs):
        super().patch(request, *args, **kwargs)
        return Response(
            {'success': 'Telegram ID updated successfully'},
            status=status.HTTP_200_OK
        )


# class TranslateMovieGenericAPIView(GenericAPIView):
#     serializer_class = TranslateMovieModelSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'status': 'success'}, status=status.HTTP_200_OK)


@extend_schema(tags=['User-chat'])
class UserMessageModelViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = UserMessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        chat, _ = Chat.objects.get_or_create(user=self.request.user)
        serializer.save(chat=chat)


@extend_schema(tags=['Admin-chat'])
class AdminMessageModelViewSet(ModelViewSet):
    queryset = AdminAnswer.objects.all()
    serializer_class = AdminMessageSerializer
    permission_classes = [IsAdminUser]




@extend_schema(tags=['news'])
class NewsModelViewSet(ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsModelSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]



@extend_schema(tags=['auth'])
class UserLastSearchListView(ListAPIView):
    queryset = LastSearch.objects.all()
    serializer_class = UserSearchModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


@extend_schema(tags=['Translate-Movies'])
class TranslateMoviesListAPIView(NonePaginationListAPIView):
    queryset = TranslateMovies.objects.all()
    serializer_class = TranslateMovieModelSerializer


@extend_schema(tags=['Translate-Movies'])
class PaymentTranslateMoviesListCreateAPIView(CreateAPIView):
    queryset = PaymentTranslateMovie.objects.all()
    serializer_class = PaymentTranslateMovieModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        telegram_id = serializer.validated_data.get('telegram_id')
        amount = serializer.validated_data.get('amount')
        translate_movie = serializer.validated_data.get('translate_movie')

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({'message': 'Telegram ID does not exist'}, status=status.HTTP_404_NOT_FOUND)

        movie = get_object_or_404(TranslateMovies, id=translate_movie.id)

        with transaction.atomic():
            if user.balance < amount:
                return Response({'message': 'Not Enough Money!'}, status=status.HTTP_400_BAD_REQUEST)

            user.balance -= amount
            movie.collected_money += amount

            user.save(update_fields=['balance'])
            movie.save(update_fields=['collected_money'])

            serializer.save(user=user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Donate'])
class TopDonatersListAPIView(NonePaginationListAPIView):
    serializer_class = TopDonaterModelSerializer

    def get_queryset(self):
        return (
            PaymentTranslateMovie.objects
            .values('user', 'user__username')
            .annotate(donat=Sum('amount'))
            .order_by('-donat')[:10]
        )


@extend_schema(tags=['Donate'])
class LastDonatesListAPIView(NonePaginationListAPIView):
    queryset = PaymentTranslateMovie.objects.all().order_by('-created_at')[:10]
    serializer_class = LastDonatesModelSerializer



