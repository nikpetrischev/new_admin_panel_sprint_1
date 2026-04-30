import uuid

from django.core.validators import MaxValueValidator, MinValueValidator, MaxLengthValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True 


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(
        _('name'),
        blank=False,
        max_length=32,
    )
    description = models.TextField(
        _('description'),
        blank=False,
        null=True,
        max_length=1024,
    )

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __str__(self) -> str:
        return self.name
    

class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField(
        _('full_name'),
        blank=False,
        max_length=256,
    )
    
    class Meta:
        db_table = "content\".\"person"
        indexes = [
            models.Index(fields=['full_name'], name='person_full_name_idx'),
        ]
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')

    def __str__(self) -> str:
        return self.full_name
    

class FilmWork(UUIDMixin, TimeStampedMixin):
    title = models.TextField(_('title'), blank=False)
    description = models.TextField(
        _('description'),
        blank=False,
        null=True,
        max_length=1024,
    )
    creation_date = models.DateField(_('creation_date'))
    rating = models.FloatField(
        _('rating'),
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )
    type = models.CharField(_('type'), blank=False, max_length=128)
    
    genres = models.ManyToManyField(Genre, through='GenreFilmWork')
    persons = models.ManyToManyField(Person, through='PersonFilmWork')

    class Meta:
        db_table = "content\".\"film_work"
        indexes = [
            models.Index(fields=['creation_date'], name='film_work_creation_date_idx'),
            models.Index(fields=['type'], name='film_work_type_idx'),
            models.Index(fields=['rating'], name='film_work_rating_idx'),
        ]
        verbose_name = _('Filmwork')
        verbose_name_plural = _('Filmowrks')

    def __str__(self) -> str:
        return self.title

   
class GenreFilmWork(UUIDMixin):
    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['film_work', 'genre'],
                name='film_work_genre_idx',
            ),
        ]
        db_table = "content\".\"genre_film_work" 


class PersonFilmWork(UUIDMixin):
    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.TextField('role')
    created = models.DateTimeField(auto_now_add=True) 

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['film_work', 'person', 'role'],
                name='film_work_person_role_idx',
            ),
        ]
        db_table = "content\".\"person_film_work"
