from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from django.forms import DateInput, ModelForm

from .models import Comment, Post

User = get_user_model()


class ProfileChangeForm(UserChangeForm):
    """
    User model form.

    Fields:
    * username;
    * first_name;
    * last_name;
    * email.
    """

    password = None

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
        )


class PostForm(ModelForm):
    """
    Post model form.

    Includes all fields exept: `author` and `is_published`.
    """

    class Meta:
        model = Post
        exclude = (
            'author',
            'is_published',
        )
        widgets = {
            'pub_date': DateInput({'type': 'date'}),
        }


class CommentForm(ModelForm):
    """
    Comment model form.

    Includes only `text` field.
    """

    class Meta:
        model = Comment
        fields = ('text',)
