import datetime

import django
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta

from mysite import settings
from .models import Question, Choice


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
        self.assertListEqual(list(
            response.context["latest_question_list"]),
            [])

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 302 not found.
        """
        future_question = create_question(
            question_text="Future question.",
            days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(
            question_text="Past Question.",
            days=-5)
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
        self.assertListEqual(
            list(response.context["latest_question_list"]),
            [question]
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertListEqual(
            list(response.context["latest_question_list"]),
            [question2, question1]
        )


class QuestionModelTests(TestCase):
    def test_is_published_future_date(self):
        """Questions with a future pub_date are not published."""
        future_question = Question(
            pub_date=timezone.now() + timedelta(days=30))
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
        future_question = Question(
            pub_date=timezone.now() + timedelta(days=30))
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

    def test_can_vote_without_end_date(self):
        """Can vote if there is no end_date and pub_date is in the past."""
        question = Question(
            pub_date=timezone.now() - timedelta(days=1)
        )
        self.assertTrue(question.can_vote())


class UserAuthTest(django.test.TestCase):

    def setUp(self):
        """Set up a user, question, and choices for testing."""
        super().setUp()
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@nowhere.com"
        )
        self.user1.first_name = "Tester"
        self.user1.save()

        # Create a question and a few choices
        self.question = (Question.objects.create
                         (question_text="First Poll Question"))
        self.choice1 = (Choice.objects.create
                        (question=self.question, choice_text="Choice 1"))
        self.choice2 = (Choice.objects.create
                        (question=self.question, choice_text="Choice 2"))

    def test_logout(self):
        """A user can logout using the logout URL."""
        logout_url = reverse("logout")
        self.assertTrue(self.client.
                        login(username=self.username, password=self.password))

        response = self.client.post(logout_url)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_login_view(self):
        """A user can login using the login view."""
        login_url = reverse("login")
        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)

        form_data = {"username": self.username, "password": self.password}
        response = self.client.post(login_url, form_data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_auth_required_to_vote(self):
        """Authentication is required to submit a vote."""
        vote_url = reverse('polls:vote', args=[self.question.id])
        form_data = {"choice": f"{self.choice1.id}"}
        response = self.client.post(vote_url, form_data)
        self.assertEqual(response.status_code, 302)
        login_with_next = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, login_with_next)

    def test_authenticated_user_can_vote(self):
        """Authenticated users can vote on a poll."""
        self.client.login(username=self.username, password=self.password)
        vote_url = reverse("polls:vote", args=(self.question.id,))
        response = self.client.post(vote_url, {'choice': self.choice1.id})
        self.assertEqual(response.status_code, 302)
        self.assertIn('results', response.url)

    def test_user_can_vote_only_once(self):
        """Authenticated users can only vote once."""
        self.client.login(username=self.username, password=self.password)
        vote_url = reverse("polls:vote", args=(self.question.id,))
        self.client.post(vote_url, {'choice': self.choice1.id})
        self.assertEqual(self.choice1.votes, 0)
        self.assertEqual(self.choice2.votes, 1)

    def test_user_can_change_vote(self):
        """Authenticated users can change their vote."""
        self.client.login(username=self.username, password=self.password)
        vote_url = reverse("polls:vote", args=(self.question.id,))
        self.client.post(vote_url, {'choice': self.choice1.id})
        self.client.post(vote_url, {'choice': self.choice2.id})
        self.assertEqual(self.choice1.votes, 0)
        self.assertEqual(self.choice2.votes, 1)

    def test_show_previous_vote(self):
        """Show the user's previous vote when they view the poll."""
        (self.client.login
         (username=self.username, password=self.password))
        (self.client.post
         (reverse("polls:vote",
                  args=(self.question.id,)),
          {'choice': self.choice1.id}))
        response = (self.client.get
                    (reverse("polls:detail", args=(self.question.id,))))
        self.assertContains(response, 'checked', count=1)
