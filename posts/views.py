from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import PostForm
from .models import Post


class CreatePostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'main/index.html'
    success_url = reverse_lazy('recognition')
