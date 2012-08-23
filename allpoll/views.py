from datetime import date

from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, render, redirect

from allpoll.models import Poll, Choice, Vote
from allpoll.protection import can_vote, mark_voted


class PollListView(ListView):
    template_name = 'allpoll/list.html'
    context_object_name = 'poll_list'
    paginate_by = 20

    def get_queryset(self):
        queryset = Poll.objects.public()
        for poll in queryset:
            poll.can_vote = can_vote(self.request, poll)
        return queryset

poll_list = PollListView.as_view()


def poll_vote(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    context = {'poll': poll}

    if request.method == 'POST':
        if not can_vote(request, poll):
            return HttpResponseForbidden()
        try:
            choice_id = int(request.POST.get('choice_id'))
        except TypeError, ValueError:
            raise Http404()

        choice = get_object_or_404(Choice, poll=poll, id=choice_id)
        choice.vote()

        if request.is_ajax():
            response = render(request, 'allpoll/block_result.html', context)
        else:
            response = redirect('.')
        mark_voted(request, response, poll)
    else:
        if 'result' in request.GET or not can_vote(request, poll):
            template = 'allpoll/result.html'
        else:
            template = 'allpoll/vote.html'

        response = render(request, template, context)

    return response