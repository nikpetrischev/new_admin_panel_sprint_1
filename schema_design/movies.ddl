CREATE SCHEMA IF NOT EXISTS content;

-- Creating tables

CREATE TABLE IF NOT EXISTS content.film_work (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE NOT NULL,
    rating FLOAT,
    type TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CHECK (LENGTH(description) < 1024),
    CHECK (LENGTH(type) < 128),
    CHECK (rating BETWEEN 0 AND 100)
);

CREATE TABLE IF NOT EXISTS content.person (
    id UUID PRIMARY KEY,
    full_name TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CHECK (LENGTH(full_name) < 256)
);

CREATE TABLE IF NOT EXISTS content.genre (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CHECK (LENGTH(name) < 32),
    CHECK (LENGTH(description) < 1024)
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id UUID PRIMARY KEY,
    person_id UUID NOT NULL REFERENCES content.person(id),
    film_work_id UUID NOT NULL REFERENCES content.film_work(id),
    role TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CHECK (LENGTH(role) < 128)
);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id UUID PRIMARY KEY,
    genre_id UUID NOT NULL REFERENCES content.genre(id),
    film_work_id UUID NOT NULL REFERENCES content.film_work(id),
    created TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Creating indexes

CREATE INDEX IF NOT EXISTS film_work_creation_date_idx ON content.film_work(creation_date);
CREATE INDEX IF NOT EXISTS film_work_rating_idx ON content.film_work(rating);
CREATE INDEX IF NOT EXISTS film_work_type_idx ON content.film_work(type);

CREATE INDEX IF NOT EXISTS person_full_name_idx ON content.person(full_name);

CREATE UNIQUE INDEX IF NOT EXISTS film_work_person_role_idx ON content.person_film_work(film_work_id, person_id, role);
-- ^ Такая постановка позволит конкретному человеку участвовать в одной картине более одного раза,
-- главное чтобы в разных "ролях" (актёр и продюссер, например)
CREATE UNIQUE INDEX IF NOT EXISTS film_work_genre_idx ON content.genre_film_work(film_work_id, genre_id);