from django.contrib.auth.hashers import check_password
from django.db.models import Q, PositiveIntegerField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, CharField, EmailField
from rest_framework.generics import CreateAPIView
from rest_framework.serializers import ModelSerializer, IntegerField, Serializer

from app.models.orders import Purchase, PurchaseMovie, Notification, Payment, OrderSubscription, \
    PaymentSubscription, OrderSubscriptionItem, PaymentTranslateMovie
from app.models.movie import Movie, Category, CastMembers, Genre, MovieCast, Subscribers, LastSearch, \
    SubscriptionItems, MovieComment, Message, AdminAnswer, News, FavouriteMovies, TranslateMovies

from app.models.users import User




class GenreModelSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']



class CommentModelSerializer(ModelSerializer):
    class Meta:
        model = MovieComment
        fields = ['id', 'movie', 'user', 'comment', 'created_at']



class MovieModelSerializer(ModelSerializer):

    total_comments = IntegerField(read_only=True)

    class Meta:
        model = Movie
        fields = ['id', 'picture', 'title', 'slug', 'views', 'rate', 'total_comments']



class MovieDetailModelSerializer(ModelSerializer):
    genre = GenreModelSerializer(many=True, read_only=True)
    similar_movies = SerializerMethodField()
    movie_comment = SerializerMethodField()


    class Meta:
        model = Movie
        fields = ['id', 'picture', 'title', 'genre', 'country', 'release_date',
                  'language', 'duration', 'trailer_url', 'video', 'similar_movies', 'subscribe',
                  'movie_comment', 'views']

    def get_similar_movies(self, obj):
        queryset = Movie.objects.exclude(id=obj.id)
        genre_ids = obj.genre.values_list('id', flat=True)
        genre_matches = queryset.filter(genre__in=genre_ids)

        title_matches = queryset.filter(title__icontains=obj.title.split()[0])

        similar = (genre_matches | title_matches).distinct()[:5]
        return MovieModelSerializer(similar, many=True).data


    def get_movie_comment(self, obj):
        queryset = MovieComment.objects.filter(movie=obj.id)

        return CommentModelSerializer(queryset, many=True).data




class SubscriptionVariantsModelSerializer(ModelSerializer):
    class Meta:
        model = SubscriptionItems
        fields = ['id', 'subscribe', 'valid_until_days', 'price']


class PurchaseMovieModelSerializer(ModelSerializer):
    movie_price = SerializerMethodField(read_only=True)

    class Meta:
        model = PurchaseMovie
        fields = ['id', 'purchase', 'movie', 'status', 'movie_price', 'created_at']

    def get_movie_price(self, obj):
        return obj.get_price


class PurchaseModelSerializer(ModelSerializer):
    movies = PurchaseMovieModelSerializer(many=True, read_only=True)

    class Meta:
        model = Purchase
        fields = ['id', 'user', 'created_at', 'movies']


class PaymentMovieModelSerializer(ModelSerializer):

    class Meta:
        model = Payment
        fields = ['id', 'purchase_movie', 'status', 'payment_method', 'created_at']


class CreateOrderForMovieModelSerializer(ModelSerializer):

    class Meta:
        model = Purchase
        fields = ['id', 'user', 'created_at']


# For Subscription


class OrderSubscriptionItemModelSerializer(ModelSerializer):

    class Meta:
        model = OrderSubscriptionItem
        fields = ['id', 'order', 'subscription', 'status', 'created_at']


class OrderSubscriptionModelSerializer(ModelSerializer):
    class Meta:
        model = OrderSubscription
        fields = ['id', 'user', 'created_at']

    def get_price(self, obj):
        return obj.get_price


class PaymentSubscriptionModelSerializer(ModelSerializer):

    price = SerializerMethodField()

    class Meta:
        model = PaymentSubscription
        fields = ['id', 'order', 'status', 'price', 'payment_method', 'created_at']

    def get_price(self, obj):
        return obj.price


class NotificationModelSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'notification_type', 'created_at']


class UserBalanceModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'balance']


class UserFillBalanceModelSerializer(ModelSerializer):
    amount = IntegerField(min_value=1)

    class Meta:
        model = User
        fields = ['amount']

    def validate_amount(self, value):
        if value > 10000000:
            raise ValidationError('Amount must be less than 10000000.')
        return value


class UserFillBalanceWithTelegramModelSerializer(Serializer):
    telegram_id = CharField(required=True)
    amount = IntegerField(required=True)

    def validate_amount(self, value):
        if value > 10000000 or value < 0:
            raise ValidationError('invalid amount (amount must not negative and > 10000000)')


class UserCheckBalanceModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['balance']


class PaymentModelSerializer(ModelSerializer):

    price = SerializerMethodField()
    class Meta:
        model = Payment
        fields = ['id', 'purchase_movie', 'status', 'payment_method', 'price', 'created_at']

    def get_price(self, obj):
        return obj.get_price


class SubscribersModelSerializer(ModelSerializer):
    expires_at = SerializerMethodField()

    class Meta:
        model = Subscribers
        fields = ['id', 'user', 'subscribe_item', 'valid_at', 'expires_at']

    def get_expires_at(self, obj):
        return obj.expires_at


# For Updating User's telegram_id from Telegram
class TelegramIDUpdateSerializer(ModelSerializer):
    username = CharField(write_only=True, required=True)
    password = CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'telegram_id']
        extra_kwargs = {
            'telegram_id': {'required': True}
        }

    def validate(self, data):
        user = User.objects.filter(username=data['username']).first()

        if not user:
            raise ValidationError("User not found")

        if not check_password(data['password'], user.password):
            raise ValidationError("Invalid password")

        if user.telegram_id:
            raise ValidationError("Telegram ID already exists")

        return {'user': user, 'telegram_id': data['telegram_id']}


class PreRegisterSerializer(Serializer):
    username = CharField()
    email = EmailField()
    password = CharField(write_only=True)


    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        return value


class OTPVerifySerializer(Serializer):
    email = EmailField()
    code = CharField(max_length=6)


class UserLoginSerializer(Serializer):
    username_or_email = CharField()
    password = CharField()

    def validate(self, attrs):
        identifier = attrs.get('username_or_email')
        password = attrs.get('password')

        user = User.objects.filter(Q(email=identifier) | Q(username=identifier)).first()

        print(user.check_password(password))

        if not user:
            raise ValidationError("User not found.")

        if not user.check_password(password):
            raise ValidationError("Incorrect password.")

        if not user.is_active:
            raise ValidationError("User is inactive.")

        attrs['user'] = user
        return attrs


class AdminAnswerSerializer(ModelSerializer):
    class Meta:
        model = AdminAnswer
        fields = ['id', 'answer', 'created_at']


class UserMessageSerializer(ModelSerializer):
    answers = AdminAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'message', 'created_at', 'answers']




class AdminMessageSerializer(ModelSerializer):
    message_text = SerializerMethodField()
    message_created_at = SerializerMethodField()

    class Meta:
        model = AdminAnswer
        fields = ['id', 'message', 'message_text', 'message_created_at', 'answer', 'created_at']

    def get_message_text(self, obj):
        return obj.message.message

    def get_message_created_at(self, obj):
        return obj.message.created_at




class NewsModelSerializer(ModelSerializer):
    class Meta:
        model = News
        fields = ['id', 'title', 'trailer_url', 'description', 'created_at']


class FavouritesMoviesModelSerializer(ModelSerializer):
    class Meta:
        model = FavouriteMovies
        fields = ['id', 'movie', 'user', 'created_at']



class TranslateMovieDetailModelSerializer(ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'picture', 'title', 'description']


class TranslateMovieModelSerializer(ModelSerializer):

    movie = TranslateMovieDetailModelSerializer(read_only=True, many=False)
    left = SerializerMethodField()

    class Meta:
        model = TranslateMovies
        fields = ['id', 'movie', 'movie_fund', 'collected_money', 'left', 'is_finish', 'created_at']


    def get_left(self, obj):
        return obj.left


class PaymentTranslateMovieModelSerializer(ModelSerializer):
    telegram_id = CharField(write_only=True)

    class Meta:
        model = PaymentTranslateMovie
        fields = ['id', 'telegram_id', 'translate_movie', 'amount', 'created_at']

    def create(self, validated_data):
        telegram_id = validated_data.pop('telegram_id', None)

        return PaymentTranslateMovie.objects.create(**validated_data)


class UserSearchModelSerializer(ModelSerializer):
    class Meta:
        model = LastSearch
        fields = ['id', 'user', 'search', 'created_at']



class UpdateTranslateMovieStatusModelSerializer(Serializer):
    movie = CharField(max_length=100)
    telegram_id = CharField(max_length=100)



class TopDonaterModelSerializer(Serializer):

    user = IntegerField()
    username = CharField(source='user__username')
    donat = IntegerField()


class LastDonatesModelSerializer(ModelSerializer):

    class Meta:
        model = PaymentTranslateMovie
        fields = ['id', 'user', 'amount', 'created_at']