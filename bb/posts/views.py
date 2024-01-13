# Импортирую класс, который говорит о том, что в этом представлении будет выводиться список объектов из БД
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy, resolve
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.conf import settings

from .models import Post, Category, Author, Reply
from .forms import PostForm, ReplyForm


# Личная страница пользователя
class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Получаю посты, автором которых является текущий пользователь
        posts = Post.objects.filter(author__user=user)
        # Получаю отзывы к этим постам
        replies = Reply.objects.filter(post__in=posts)
        # Получаю тайтлы постов
        post_titles = Post.objects.filter(id__in=posts.values_list('id', flat=True)).values_list('title',
                                                                                                 flat=True).distinct()
        # Получаю значение тайтла из параметра GET запроса
        selected_title = self.request.GET.get('post_title', None)
        # Фильтрую отклики по выбранному тайтлу
        if selected_title:
            replies = replies.filter(post__title=selected_title)
        context['replies'] = replies
        context['post_titles'] = post_titles
        return context

    def post(self, request, *args, **kwargs):
        reply_id = request.POST.get('reply_id')
        action = request.POST.get('action')

        if action == 'accept':
            self.accept_reply(reply_id, request)
        elif action == 'delete':
            self.delete_reply(reply_id)

        return redirect('account_info')

    def accept_reply(self, reply_id, request):
        reply = Reply.objects.get(id=reply_id)
        reply.status = 'received'
        reply.save()

        # Определяю пользователя, оставившего отклик, автора и тайтл поста
        reviewer = reply.user
        post_author = reply.post.author.user
        post_title = reply.post.title
        subject = 'Ваш отклик принят'

        html = render_to_string(
            'mail/reply_received.html',
            {
                'reviewer': reviewer,
                'post_author': post_author,
                'post_title': post_title,
            }
        )

        # Отправляю уведомления пользователю, оставившему отклик
        msg = EmailMultiAlternatives(
            subject=subject,
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reviewer.email],
        )
        msg.attach_alternative(html, "text/html")
        try:
            msg.send()
        except Exception as e:
            print(e)
        return redirect(request.META.get('HTTP_REFERER'))

    def delete_reply(self, reply_id):
        reply = Reply.objects.get(id=reply_id)
        reply.delete()


# Отображение всех постов
class PostList(ListView):
    model = Post
    ordering = ['-time_in']  # Устанавливаю сортировку от новых записей к ранним
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10  # задаю количество записей на странице


# Развёрнутое отображение конкретного поста
class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


# Отображение постов по категории
class PostCategory(ListView):
    model = Post
    ordering = ['-time_in']
    template_name = 'category.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.id = resolve(self.request.path_info).kwargs['pk']
        category = Category.objects.get(id=self.id)
        queryset = Post.objects.filter(category=category)
        return queryset


# Создание поста
class PostCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = reverse_lazy('post_list')
    permission_required = 'posts.add_post'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = Author.objects.get(user=self.request.user)
        category_name = self.request.POST.get('category', None)
        category, created = Category.objects.get_or_create(name=category_name)
        post.save()
        post.category.set([category])
        return redirect(self.success_url)


# Изменение поста
class PostUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = reverse_lazy('post_list')
    permission_required = 'posts.change_post'

    def form_valid(self, form):
        post = form.save(commit=False)
        category_name = self.request.POST.get('category', None)
        category, created = Category.objects.get_or_create(name=category_name)
        post.category.clear()
        post.category.set([category])
        post.save()
        return redirect(self.success_url)


# Удаление поста
class PostDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')
    permission_required = 'posts.delete_post'


# Создание отклика
class ReplyCreate(LoginRequiredMixin, FormView):
    model = Post
    template_name = 'reply.html'
    form_class = ReplyForm
    success_url = reverse_lazy('post_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = Post.objects.get(pk=self.kwargs['pk'])
        context['post_title'] = post.title
        return context

    def form_valid(self, form):
        post = Post.objects.get(pk=self.kwargs['pk'])
        user = self.request.user
        text = form.cleaned_data['text']

        reply = Reply.objects.create(post=post, user=user, text=text)
        return redirect(self.success_url)
