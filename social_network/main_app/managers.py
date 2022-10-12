from django.db import models


class PostQuerySet(models.QuerySet):
    def friends_posts(self, user):
        return self.filter(owner__friends=user)[::-1]

    def get_posts(self, user):
        return self.filter(owner=user)[::-1]


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def friends_posts(self, user):
        return self.get_queryset().friends_posts(user)

    def get_posts(self, user):
        return self.get_queryset().get_posts(user)
