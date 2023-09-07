from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model
from django.forms import ModelForm, DateInput

from .models import Post

User = get_user_model()


class ProfileChangeForm(UserChangeForm):
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
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': DateInput({'type': 'date'}),
        }
