from abc import ABC
from datetime import datetime
import uuid
from dataclasses import dataclass, field


@dataclass(slots=True)
class BaseEntity(ABC):
    id: uuid.UUID
    created_at: datetime

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = uuid.UUID(self.id)


@dataclass(slots=True)
class FilmWork(BaseEntity):
    title: str
    description: str
    creation_date: str
    rating: float
    type: str
    file_path: str
    updated_at: datetime

    def __post_init__(self):
        BaseEntity.__post_init__(self)
        if self.description and len(self.description) > 1024:
            self.description = self.description[0:1020] + '...'


@dataclass(slots=True)
class Genre(BaseEntity):
    name: str
    description: str
    updated_at: datetime

    def __post_init__(self):
        BaseEntity.__post_init__(self)
        if self.description and len(self.description) > 1024:
            self.description = self.description[0:1020] + '...'


@dataclass(slots=True)
class Person(BaseEntity):
    full_name: str
    updated_at: datetime


@dataclass(slots=True)
class GenreFilmWork(BaseEntity):
    genre_id: uuid.UUID = field(default_factory=uuid.uuid4)
    film_work_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(slots=True)
class PersonFilmWork(BaseEntity):
    role: str
    person_id: uuid.UUID = field(default_factory=uuid.uuid4)
    film_work_id: uuid.UUID = field(default_factory=uuid.uuid4)
