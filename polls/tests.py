import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
from .models import Question


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 302 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question],
            transform=lambda x: x  # Make sure the query set elements are compared correctly
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question2, question1],
            transform=lambda x: x
        )


class QuestionModelTests(TestCase):
    def test_is_published_future_date(self):
        """Questions with a future pub_date are not published."""
        future_question = Question(pub_date=timezone.now() + timedelta(days=30))
        self.assertFalse(future_question.is_published())

    def test_is_published_default_date(self):
        """Questions with the default pub_date (now) are published."""
        current_question = Question()
        self.assertTrue(current_question.is_published())

    def test_is_published_past_date(self):
        """Questions with a past pub_date are published."""
        past_question = Question(pub_date=timezone.now() - timedelta(days=30))
        self.assertTrue(past_question.is_published())

    def test_can_vote_before_pub_date(self):
        """Cannot vote if the current date is before the pub_date."""
        future_question = Question(pub_date=timezone.now() + timedelta(days=30))
        self.assertFalse(future_question.can_vote())

    def test_can_vote_between_pub_and_end_date(self):
        """Can vote if the current date is between pub_date and end_date."""
        question = Question(
            pub_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1)
        )
        self.assertTrue(question.can_vote())

    def test_can_vote_after_end_date(self):
        """Cannot vote if the end_date is in the past."""
        past_question = Question(
            pub_date=timezone.now() - timedelta(days=2),
            end_date=timezone.now() - timedelta(days=1)
        )
        self.assertFalse(past_question.can_vote())
