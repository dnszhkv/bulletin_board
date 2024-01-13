from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from .models import Reply


@receiver(post_save, sender=Reply)
def send_reply_notification(sender, instance, **kwargs):
    # Проверяю, был ли отзыв создан (а не изменен или удален)
    if kwargs.get('created', False):
        post = instance.post
        author = post.author.user
        subject = 'Новый отзыв к вашему посту'

        # Использую render_to_string для формирования HTML-тела письма
        html = render_to_string(
            'mail/new_reply.html',
            {
                'author': author,
                'post_title': post.title,
            }
        )

        # Отправляю уведомление на почту автора поста
        msg = EmailMultiAlternatives(
            subject=subject,
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[author.email],
        )
        msg.attach_alternative(html, "text/html")
        msg.send()