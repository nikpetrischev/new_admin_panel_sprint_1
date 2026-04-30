from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Genre, PersonFilmWork


class RoleFilter(admin.SimpleListFilter):
    title = _('role')
    parameter_name = 'role'

    def lookups(self, request, model_admin):
        roles = (
            PersonFilmWork.objects
            .order_by('role')
            .values_list('role', flat=True)
            .distinct()
        )
        return [(role, role) for role in roles if role]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(personfilmwork__role=self.value()).distinct()
        return queryset
    

class GenreFilter(admin.SimpleListFilter):
    title = _('genre')
    parameter_name = 'genre'

    def lookups(self, request, model_admin):
        genres = (
            Genre.objects
            .order_by('name')
            .values_list('name', flat=True)
            .distinct()
        )
        return [(genre, genre) for genre in genres if genre]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(genres__name=self.value()).distinct()
        return queryset
