from datetime import timedelta

from django.db.models import Model, CharField, TextField, ForeignKey, FileField, ImageField, \
    CASCADE, URLField, ManyToManyField, DecimalField, DateField, DurationField, SlugField, BooleanField, \
    PositiveBigIntegerField, DateTimeField, PositiveSmallIntegerField, PositiveIntegerField, OneToOneField
from django.db.models import TextChoices
from django.utils import timezone
from django.utils.text import slugify

from app.models.base import TimeModelBase



class Category(Model):
    name = CharField(max_length=100)

    def __str__(self):
        return self.name


class Genre(Model):
    name = CharField(max_length=100)

    def __str__(self):
        return self.name


class Language(Model):
    name = CharField(max_length=100)

    def __str__(self):
        return self.name


class Countries(Model):
    name = CharField(max_length=100)

    def __str__(self):
        return self.name


class Subscriptions(TimeModelBase):
    name = CharField(max_length=100)
    description = TextField(max_length=512)
    available_movies = PositiveBigIntegerField(default=10)
    is_active = BooleanField(default=True)


    def __str__(self):
        return self.name


class SubscriptionItems(Model):
    subscribe = ForeignKey('Subscriptions', on_delete=CASCADE)
    valid_until_days = PositiveSmallIntegerField(default=30)
    price = DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.subscribe.name} - {self.valid_until_days} days'


class Subscribers(Model):
    user = ForeignKey('User', on_delete=CASCADE)
    subscribe_item = ForeignKey(
        'SubscriptionItems',
        on_delete=CASCADE,
        related_name='subscriber_items'
    )
    valid_at = DateTimeField(auto_now_add=True)
    is_active = BooleanField(default=True)

    class Meta:
        unique_together = [('user', 'subscribe_item')]

    @property
    def expires_at(self):
        return self.valid_at + timedelta(days=self.subscribe_item.valid_until_days)

    def is_subscription_valid(self):
        expiry = self.valid_at + timedelta(days=self.subscribe_item.valid_until_days)
        return self.is_active and expiry >= timezone.now()


    def __str__(self):
        return f"{self.user} - {self.subscribe_item}"



class Movie(TimeModelBase):
    class AccessType(TextChoices):
        FREE = 'FREE', 'free'
        SUBSCRIPTION = 'SUBSCRIPTION', 'subscription'
        PURCHASE = 'PURCHASE', 'purchase'



    category = ForeignKey('Category', on_delete=CASCADE)

    title = CharField(max_length=100)
    slug = SlugField(max_length=100, unique=True, editable=False)
    description = TextField(max_length=512)
    video = FileField(blank=True, null=True)
    trailer_url = URLField()
    picture = ImageField()
    rate = PositiveBigIntegerField(db_default=0)
    genre = ManyToManyField('Genre')
    country = ForeignKey('Countries', on_delete=CASCADE)
    language = ForeignKey('Language', on_delete=CASCADE)
    price = DecimalField(max_digits=5, decimal_places=2, default=0, blank=True, null=True)
    release_date = DateField()
    duration = DurationField(null=True, blank=True)
    access_type = CharField(max_length=20, choices=AccessType, db_default=AccessType.FREE)
    subscribe = ForeignKey('Subscriptions', on_delete=CASCADE, null=True, blank=True)
    is_premier = BooleanField(default=False)
    views = PositiveBigIntegerField(db_default=0)

    @property
    def get_cast(self):
        return self.cast.get_id

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):  # noqa
        title_slug = slugify(self.title, allow_unicode=True)

        self.slug = f"{title_slug}"
        while self.__class__.objects.filter(slug=self.slug).exists():
            self.slug += '-1'

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class MovieCast(TimeModelBase):
    movie = ForeignKey('Movie', on_delete=CASCADE, related_name='cast')
    movie_title = CharField(max_length=100)

    def __str__(self):
        return self.movie_title


class CastMembers(Model):
    class Roles(TextChoices):
        ACTOR = 'ACTOR', 'actor'
        REJISSOR = 'REJISSOR', 'rejissor'
        DIRECTOR = 'DIRECTOR', 'director'

    movie_cast = ForeignKey('MovieCast', on_delete=CASCADE, related_name='members')
    picture = ImageField()
    name = CharField(max_length=100)
    role = CharField(max_length=10, choices=Roles.choices, db_default=Roles.ACTOR)

    def __str__(self):
        return self.name


class Season(Model):
    movie = ForeignKey('Movie', on_delete=CASCADE, related_name='seasons')
    season_number = PositiveIntegerField()

    def __str__(self):
        return f"Season {self.season_number} - {self.movie.title}"


class Episode(Model):
    season = ForeignKey('Season', on_delete=CASCADE, related_name='episodes')
    title = CharField(max_length=100)
    video = FileField()
    duration = DurationField()

    def __str__(self):
        return f"{self.title} (Season {self.season.season_number})"



class MovieComment(TimeModelBase):
    user = ForeignKey('User', on_delete=CASCADE)
    movie = ForeignKey('Movie', on_delete=CASCADE, related_name='comments')
    comment = TextField(max_length=512)
    likes = PositiveIntegerField(db_default=0)


    def __str__(self):
        return self.comment


class Chat(TimeModelBase):
    user = ForeignKey('User', on_delete=CASCADE, related_name='user')

    def __str__(self):
        return f"{self.user} created chat!"


class Message(TimeModelBase):
    chat = ForeignKey('Chat', on_delete=CASCADE)
    message = TextField(max_length=512)

    @property
    def get_answers(self):
        return self.answers.all()

    def __str__(self):
        return f"{self.chat} - {self.message}"



class AdminAnswer(TimeModelBase):
    message = ForeignKey('Message', on_delete=CASCADE, related_name='answers')
    answer = TextField(max_length=512)

    def __str__(self):
        return f"{self.message} - {self.answer}"




class News(TimeModelBase):
    title = CharField(max_length=100)
    trailer_url = URLField()
    description = TextField()

    def __str__(self):
        return f"{self.title} - {self.trailer_url}"

    class Meta:
        ordering = ['-created_at']




class FavouriteMovies(TimeModelBase):
    movie = ForeignKey('Movie', on_delete=CASCADE)
    user = ForeignKey('User', on_delete=CASCADE)

    def __str__(self):
        return f"{self.movie} - {self.user}"

    class Meta:
        ordering = ['-created_at']
        unique_together = ['movie']


class TranslateMovies(TimeModelBase):

    movie = ForeignKey('Movie', on_delete=CASCADE, unique=True)
    movie_fund = PositiveBigIntegerField(db_default=0)
    collected_money = PositiveBigIntegerField(default=0)
    is_finish = BooleanField(default=False)

    @property
    def left(self):
        left = self.movie_fund - self.collected_money
        if left < 0:
            return 0
        return left


    def __str__(self):
        return self.movie.title

    class Meta:
        ordering = ['-created_at']



class LastSearch(TimeModelBase):
    user = ForeignKey('User', on_delete=CASCADE)
    search = CharField(max_length=50)


    def __str__(self):
        return f"{self.user} Search: {self.search}"


    class Meta:
        ordering = ['-created_at']