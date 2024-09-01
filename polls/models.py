import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    """A question object with a question_text and a publication date."""
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published", default=timezone.now)
    end_date = models.DateTimeField("end date", null=True, blank=True)

    def was_published_recently(self):
        """Returns True if the question was published within the last day."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """Check if the question is published. Returns True if current date is on or after publication date."""
        return timezone.now() >= self.pub_date

    def can_vote(self):
        """Check if voting is allowed for this question.Returns True if current date is between pub_date and end_date"""
        now = timezone.now()
        if self.end_date:
            return self.pub_date <= now <= self.end_date
        return self.pub_date <= now

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

