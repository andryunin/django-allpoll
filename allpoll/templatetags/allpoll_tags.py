from django import template
from django.http import HttpRequest

from allpoll import settings
from allpoll.models import Poll
from allpoll.protection import can_vote


register = template.Library()


class AllPollNode(template.Node):
    def __init__(self, condition):
        self.condition = condition

    def get_poll(self):
        try:
            if self.condition == 'latest':
                poll = Poll.objects.public().latest()
            elif self.condition == 'random':
                poll = Poll.objects.public().order_by('?')[0]
        except (Poll.DoesNotExist, IndexError), e:
            return None
        else:
            return poll

    def render(self, context):
        if not isinstance(context.get('request'), HttpRequest):
            raise template.VariableDoesNotExist(
                'Not found request object in template context.' +
                'Please add `django.core.context_processors.request` to ' +
                'TEMPLATE_CONTEXT_PROCESSORS tuple in settings.py'
            )

        poll = self.get_poll()
        if poll:
            poll.can_vote = can_vote(context['request'], poll)
            return self.allpoll_render(context, poll)
        return ''

    def allpoll_render(self, context, poll):
        raise NotImplementedError()


class AllPollGetNode(AllPollNode):
    def __init__(self, condition, varname):
        super(AllPollGetNode, self).__init__(condition)
        self.varname = varname

    def allpoll_render(self, context, poll):
        context[self.varname] = poll
        return ''


class AllPollRenderNode(AllPollNode):
    def allpoll_render(self, context, poll):
        if poll.can_vote:
            tpl = template.loader.get_template('allpoll/block_vote.html')
        else:
            tpl = template.loader.get_template('allpoll/block_result.html')
        return tpl.render(template.Context({'poll': poll}))


@register.tag(name='allpoll_get')
def do_get(parser, token):
    """
    Adds poll object to template context.

    Examples:
        {% allpoll_get latest as poll %}
        {% allpoll_get random as poll %}
    Where poll - name of variable will be added to context.

    Please note that tag does not render poll itself but only add it to context.
    Example with rendering may looks like this:
    
        {% allpoll_get latest as poll %}
        {% if poll %}
          {% if poll.can_vote %}
            {% include "allpoll/block_vote.html %}
          {% else %}
            {% include "allpoll/block_result.html %}
        {% endif %}

    (But in that case you should use allpoll_render tag instead.)
    """
    try:
        name, condition, as_word, varname = token.split_contents()
        if as_word != 'as':
            raise ValueError()
    except ValueError:
        raise template.TemplateSyntaxError('tag syntax error')

    if condition not in ('latest', 'random'):
        raise template.TemplateSyntaxError('unknown condition')

    return AllPollGetNode(varname, condition)


@register.tag(name='allpoll_render')
def do_get(parser, token):
    try:
        name, condition = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('tag syntax error')

    if condition not in ('latest', 'random'):
        raise template.TemplateSyntaxError('unknown condition')

    return AllPollRenderNode(condition)