from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_object(self, queryset=None):
        """
        Return the question object, raising a 404 error if the poll is not
        yet published or does not exist.
        """
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
        # Redisplay the question voting form with an error message.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    # if the user has a vote:
    #     change the vote
    #     save the vote
    # else:
    #     create a new vote
    #     save the vote
    #

    # if request.user.votes_set.filter(choice__question=question).exists():
    #     vote = request.user.votes_set.get(choice__question=question)
    #     vote.choice = selected_choice
    #     vote.save()
    # else:
    #     vote = Votes(choice=selected_choice, user=request.user)
    #     vote.save()

    selected_choice.votes += 1
    selected_choice.save()
    request.session[f'voted_for_question_{question_id}'] = True
    # Redirect to the results page after successfully voting.
    return HttpResponseRedirect(reverse(
        'polls:results',
        args=(question.id,)))
