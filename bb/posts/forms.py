from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Post, Author, CATEGORY_CHOICES, Reply


# Автоматическое добавления зарегистрированных пользователей в группу 'authors'
class AuthorsSignupForm(SignupForm):
    def save(self, request):
        user = super(AuthorsSignupForm, self).save(request)
        # Добавляю пользователя в группу "authors"
        authors_group = Group.objects.get(name='authors')
        authors_group.user_set.add(user)
        # Создаю объект модели Author, связанный с пользователем
        Author.objects.create(name=user.username, user=user)
        return user


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].required = False

    category = forms.CharField(
        widget=forms.Select(choices=CATEGORY_CHOICES, attrs={'class': 'form-control'})
    )

    class Meta:
        model = Post
        fields = ['title', 'text', 'category']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Заголовок'}),
            'text': CKEditor5Widget(
                attrs={'class': 'django_ckeditor_5', 'placeholder': 'Текст', 'rows': 5}, config_name='text'
            ),
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['text']

        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Текст', 'rows': 5}),
        }
