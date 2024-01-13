from django.contrib.auth.models import User
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


# Определяю варианты категории для постов
TA = 'Танки'
HE = 'Хилы'
DD = 'ДД'
TR = 'Торговцы'
GM = 'Гилдмастеры'
QG = 'Квестгиверы'
BS = 'Кузнецы'
LW = 'Кожевники'
AL = 'Зельевары'
SC = 'Мастера заклинаний'

CATEGORY_CHOICES = [
    (TA, 'Танки'),
    (HE, 'Хилы'),
    (DD, 'ДД'),
    (TR, 'Торговцы'),
    (GM, 'Гилдмастеры'),
    (QG, 'Квестгиверы'),
    (BS, 'Кузнецы'),
    (LW, 'Кожевники'),
    (AL, 'Зельевары'),
    (SC, 'Мастера заклинаний'),
]


# Модель Author представляет собой информацию об авторах постов (объявлений)
class Author(models.Model):
    name = models.CharField(unique=True, max_length=255)  # Имя автора
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Связь один-к-одному с моделью User

    # Возвращает имя автора как строковое представление объекта
    def __str__(self):
        return self.name


# Модель Category - категории постов
class Category(models.Model):
    name = models.CharField(choices=CATEGORY_CHOICES, max_length=18)  # Категория (на выбор)

    def get_category(self):
        return self.name

    # Метод для отображения информации о постах на сайте
    def __str__(self):
        return self.name


# Модель Post - посты (объявления)
class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)  # Связь с моделью Author
    time_in = models.DateTimeField(auto_now_add=True)  # Дата и время создания поста
    # Связь многие-ко-многим с моделью Category через PostCategory
    category = models.ManyToManyField('Category', through='PostCategory')
    title = models.TextField(max_length=255)  # Заголовок поста
    text = CKEditor5Field('Text', config_name='extends')  # Текст поста

    # Метод для предпросмотра текста поста (первых 124 символов)
    def preview(self):
        return self.text[:124] + '...' if len(self.text) > 124 else self.text

    # Метод для отображения заголовка поста на сайте
    def __str__(self):
        return self.title


# Модель PostCategory - связь между постами и категориями
class PostCategory(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)  # Связь с моделью Post
    category = models.ForeignKey('Category', on_delete=models.CASCADE)  # Связь с моделью Category


# Модель Reply - отклики к постам
class Reply(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)  # Связь с моделью Post
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Связь с моделью User
    text = models.TextField()  # Текст отклика
    time_in = models.DateTimeField(auto_now_add=True)  # Дата и время создания отклика
