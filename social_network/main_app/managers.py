from django.db import models


class PostQuerySet(models.QuerySet):
    def reversed_filter(self, *args, **kwargs):
        result = self.filter(*args, **kwargs)

        if result.count() > 0:
            return reversed(self.filter(*args, **kwargs))
        return None

    def friends_posts(self, user):
        return self.reversed_filter(owner__friends=user)

    def get_posts(self, user):
        return self.reversed_filter(owner=user)


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def friends_posts(self, user):
        return self.get_queryset().friends_posts(user)

    def get_posts(self, user):
        return self.get_queryset().get_posts(user)
