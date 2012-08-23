from datetime import date

from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, render, redirect
from django.forms import RadioSelect

from allpoll.models import Poll, Choice, Vote
from allpoll.protection import is_voted, mark_voted


class PollListView(ListView):
    template_name = 'allpoll/list.html'
    context_object_name = 'poll_list'
    paginate_by = 20
    queryset = Poll.objects.public()

poll_list = PollListView.as_view()


def poll_vote(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    context = {'poll': poll}

    if request.method == 'POST':
        if is_voted(request, poll):
            return HttpResponseForbidden()
        try:
            choice_id = int(request.POST.get('choice_id'))
        except TypeError, ValueError:
            raise Http404()

        choice = get_object_or_404(Choice, poll=poll, id=choice_id)
        choice.vote()

        if request.is_ajax():
            response = render(request, 'allpoll/block_result.html', {
                'poll': poll,
            })
        else:
            response = redirect('.')
        mark_voted(request, response, poll)
    else:
        if 'result' in request.GET or is_voted(request, poll):
            template = 'allpoll/result.html'
        else:
            choices = [(i.id, i.answer) for i in poll.get_choices()]
            context['widget'] = RadioSelect(choices=choices).render(name='choice_id', value=1)
            template = 'allpoll/vote.html'

        response = render(request, template, context)

    return response