from datetime import date

from django.http import HttpResponse
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, render

from allpoll.models import Poll, Choice, Vote


class PollListView(ListView):
    template_name = 'allpoll/list.html'
    context_object_name = 'poll_list'
    paginate_by = 20
    queryset = Poll.objects.public()

poll_list = PollListView.as_view()


def poll_vote(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    if request.method == 'POST':
        return HttpResponse('OK')
    else:
        if 'result' in request.GET:
            template = 'allpoll/result.html'
        else:
            template = 'allpoll/vote.html'

        return render(request, template, {
            'poll': poll,
        })