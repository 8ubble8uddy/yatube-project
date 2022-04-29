from django import forms

from posts import models


class PostForm(forms.ModelForm):
    class Meta:
        model = models.Post
        fields = ['group', 'text', 'image']
        labels = {
            'text': 'Что у вас нового?',
            'group': 'Группа',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ['text']
