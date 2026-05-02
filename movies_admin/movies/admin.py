from django.contrib import admin

from .filters import GenreFilter, RoleFilter
from .models import Genre, FilmWork, Person, GenreFilmWork, PersonFilmWork


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')

    list_filter = ('name',)
    search_fields = ('name', 'description')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'created_at', 'updated_at')

    search_fields = ('full_name',)
    list_filter = (RoleFilter,)


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmWorkInline, PersonFilmWorkInline)

    list_display = ('title', 'type', 'creation_date', 'rating', 'created_at', 'updated_at')

    list_filter = ('type', GenreFilter)
    search_fields = ('title', 'description', 'creation_date')
