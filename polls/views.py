import logging

from django.contrib.auth import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Choice, Question, Vote

logger = logging.getLogger('polls')


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    logger.info(f'User {user.username} logged in from IP {get_client_ip(request)}.')


@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    logger.info(f'User {user.username} logged out from IP {get_client_ip(request)}.')


@receiver(user_login_failed)
def user_logged_in_fail_handler(sender, request, **kwargs):
    logger.warning(f' Failed login from IP {get_client_ip(request)}.')


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions (not including those set to be
        published in the future)."""
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_object(self, queryset=None):
        """Return the question object, raising a 404 error if the poll is not
        yet published or does not exist."""
        try:
            question = super().get_object(queryset)
            if question.pub_date > timezone.now():
                raise Http404("Poll does not exist")
            return question
        except Http404:
            raise Http404("The requested poll does not exist.")

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests, redirecting with an error message if the poll
        is not available for voting.
        """
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(request, "Poll not found.")
            return HttpResponseRedirect(reverse('polls:index'))

        question = get_object_or_404(Question, pk=kwargs['pk'])
        user = request.user

        if user.is_authenticated:
            try:
                selected_choice = question.choice_set.get(vote__user=user)
            except Choice.DoesNotExist:
                selected_choice = None

            context = {
                'question': question,
                'selected_choice': selected_choice,
            }
            return render(request, 'polls/detail.html', context)
        else:
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


@login_required
def vote(request, question_id):
    """Handle voting for a particular choice in a poll."""
    question = get_object_or_404(Question, pk=question_id)

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a valid choice.",
        })

    try:
        user_vote = Vote.objects.get(user=request.user, choice__question=question)
        user_vote.choice = selected_choice
    except Vote.DoesNotExist:
        user_vote = Vote.objects.create(user=request.user, choice=selected_choice)

    user_vote.save()

    messages.success(request, f"Your vote for '{selected_choice}' has been recorded.")
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


def get_client_ip(request):
    """Get the client's IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
