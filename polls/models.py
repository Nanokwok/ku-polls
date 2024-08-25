import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    """A question object with a question_text and a publication date."""
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def was_published_recently(self):
        """Returns True if the question was published within the last day."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def __str__(self):
        """Returns the question_text of the question."""
        return self.question_text


class Choice(models.Model):
    """A choice object with a choice_text and a vote count."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """Returns the choice_text of the choice."""
        return self.choice_text

