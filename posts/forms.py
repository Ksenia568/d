from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['photo']


class CreateListForm(forms.Form):
    name = forms.CharField(label="Name ", max_length=300)
