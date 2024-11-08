"""Модели приложения reviews."""
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.constants import (EMAIL_MAX_LENGTH, FIELD_MAX_LENGTH,
                               LENGTH_TO_DISPLAY, MAX_SCORE_VALUE,
                               MIN_SCORE_VALUE, USERNAME_MAX_LENGTH)
from reviews.validators import validate_year, validate_username


class BaseCategoryGenreModel(models.Model):
    """Базовая модель категории и жанра."""

    name = models.CharField(
        max_length=FIELD_MAX_LENGTH, verbose_name='Название'
    )
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    class Meta:
        ordering = ['slug']
        abstract = True

    def __str__(self):
        return self.name[:LENGTH_TO_DISPLAY]


class User(AbstractUser):
    """Модель юзера."""

    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER_ROLE = [
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
    ]

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=[validate_username]
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )
    bio = models.TextField('О себе', blank=True)
    role = models.CharField(
        'Роль',
        max_length=max(len(role[1]) for role in USER_ROLE),
        choices=USER_ROLE, default='user'
    )

    class Meta:
        """Мета класс пользователя."""

        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        """Проверка на админа."""
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        """Проверка на модератора."""
        return self.role == self.MODERATOR


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(
        max_length=FIELD_MAX_LENGTH,
        verbose_name='Название'
    )
    year = models.PositiveSmallIntegerField(
        validators=[validate_year],
        verbose_name='Год выпуска'
    )
    description = models.TextField(verbose_name='Описание')
    genre = models.ManyToManyField('Genre', through='GenreTitle',
                                   verbose_name='Жанр')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL,
                                 null=True, related_name='titles',
                                 verbose_name='Категория')

    class Meta:
        ordering = ['year']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:LENGTH_TO_DISPLAY]


class Category(BaseCategoryGenreModel):
    """Модель категории."""

    class Meta(BaseCategoryGenreModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseCategoryGenreModel):
    """Модель жанра."""

    class Meta(BaseCategoryGenreModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class GenreTitle(models.Model):
    """Связанная модель жанра и произведения."""

    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title} {self.genre}'


class Review(models.Model):
    """Модель отзыва."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(MIN_SCORE_VALUE),
            MaxValueValidator(MAX_SCORE_VALUE)
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'], name='unique_review'
            )
        ]

    def __str__(self):
        return f'Отзыв к произведению {self.title} от автора {self.author}'


class Comment(models.Model):
    """Модель комментария."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Комментарии'
        verbose_name_plural = 'Комментарий'

    def __str__(self):
        return f'Комментарий к отзыву {self.review} от автора {self.author}'
