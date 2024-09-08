from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Choice, Question, Vote


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
            question = self.get_object()
            if not question.can_vote():
                messages.error(request, "Voting is not allowed for this poll.")
                return HttpResponseRedirect(reverse('polls:index'))
            return super().get(request, *args, **kwargs)
        except Http404 as e:
            messages.error(request, str(e))
            return HttpResponseRedirect(reverse('polls:index'))


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
