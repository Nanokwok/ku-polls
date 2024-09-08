from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published", default=timezone.now)
    end_date = models.DateTimeField("end date", null=True, blank=True)

    def was_published_recently(self):
        now = timezone.now()
        return now - timezone.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        return timezone.now() >= self.pub_date

    def can_vote(self):
        now = timezone.now()
        if self.end_date:
            return self.pub_date <= now <= self.end_date
        return self.pub_date <= now

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


# class Votes(models.Model):
#     """Model to store the votes of users."""
#
#     choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(args, kwargs)
#         self.votes_set = None
#
#     @property
#     def votes(self):
#         """Return the number of votes."""
#         return self.votes_set.count()
#
#
#     def __str__(self):
#         """Return the user who voted."""
#         return self.user


