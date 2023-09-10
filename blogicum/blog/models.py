from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone

User = get_user_model()


class BaseModel(models.Model):
    """
    Abstract base model for all other blog models.

    Add is_published(Bool) and created_at(DateTime) fields.
    """

    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    """
    Posts category model.

    Fields:
    * title(Char(256));
    * description(Text);
    * slug(Slug) - slug from url;
    * is_published(Bool) - visible to users if True;
    * created_at(DateTime) - auto.
    """

    title = models.CharField(
        'Заголовок',
        max_length=256
    )
    description = models.TextField(
        'Описание'
    )
    slug = models.SlugField(
        "Идентификатор",
        unique=True,
        help_text=('Идентификатор страницы для URL; '
                   'разрешены символы латиницы, цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title


class Location(BaseModel):
    """
    Posts location model.

    Fields:
    * name(Char(256));
    * is_published(Bool) - visible to users if True
    * created_at(DateTime) - auto.
    """

    name = models.CharField(
        'Название места',
        max_length=256
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name


class PublishedPostsManager(models.Manager):
    """
    Custom manager for Post model with overriden get_queryset.
    """

    def get_queryset(self) -> QuerySet:
        """
        Return posts from table joined on Location, Category and User tables.

        Include only posts wich have `pub_date` equal or earlyer than now,
        `is_published` = True and `Category.is_published`=True.
        """
        queryset = super().get_queryset().select_related(
            'location',
            'category',
            'author'
        )
        return queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
            location__is_published=True
        )


class Post(BaseModel):
    """
    Posts category model.

    Fields:
    * title(Char(256));
    * text(Text);
    * pub_date(DateTime);
    * author(Int) - FK to Users model, cascade on delete;
    * location(Int) - FK to Location model, null on delete;
    * category(Int) - FK to Category model, null on delete;
    * is_published(Bool) - visible to users if True;
    * created_at(DateTime) - auto.
    """

    title = models.CharField(
        'Заголовок',
        max_length=256
    )
    text = models.TextField(
        'Текст'
    )
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=('Если установить дату и время в '
                   'будущем — можно делать отложенные публикации.')
    )
    author = models.ForeignKey(
        User,
        models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts'
    )
    location = models.ForeignKey(
        Location,
        models.SET_NULL,
        blank=True,
        verbose_name='Местоположение',
        null=True,
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        models.SET_NULL,
        verbose_name='Категория',
        null=True,
        related_name='posts'
    )
    image = models.ImageField(
        'Изображение',
        blank=True,
        upload_to='post_images'
    )

    objects = models.Manager()
    published_posts = PublishedPostsManager()

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.title

    def comment_count(self):
        return self.comments.count()


class Comment(models.Model):
    """
    Post comments model.

    Fields:
    * text(Text) - comment text;
    * post(Int) - FK to related Post, cascade on delete;
    * author(Int) - FK to comment author, cascade on delete;
    * created_at(DateTime) - comment creation date, auto.
    """

    text = models.TextField(
        'Текст',
    )
    post = models.ForeignKey(
        Post,
        models.CASCADE,
        verbose_name='Публикация',
        related_name='comments',
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        models.CASCADE,
        verbose_name='Автор',
        related_name='comments'
    )

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ('created_at',)
