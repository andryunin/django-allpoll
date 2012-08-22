from allpoll.models import Poll, Vote
from allpoll import settings


def is_voted(request, poll):
    # First: check logined users
    if hasattr(request, 'user') and request.user.is_authenticated():
        if Vote.objects.filter(user=request.user, poll=poll).exists():
            return True

    # Second: check cookies and session
    if hasattr(request, 'COOKIES') and poll.get_cookie_name() in request.COOKIES:
        return True
    if hasattr(request, 'session') and poll.get_cookie_name() in request.session:
        return True

    # Third: check IP addr limit
    count = Vote.objects.filter(ipaddr=request.META['REMOTE_ADDR']).count()
    if count >= settings.IP_LIMIT:
        return True
    
    return False


def mark_voted(request, response, poll):
    vote_fields = {
        'ipaddr': request.META['REMOTE_ADDR'],
        'poll': poll,
    }
    if hasattr(request, 'user') and request.user.is_authenticated():
        vote_fields['user'] = request.user

    Vote.objects.create(**vote_fields)

    response.set_cookie(
        poll.get_cookie_name(), '1',
        max_age=365 * 24 * 60 * 60, # Year
    )

    if hasattr(request, 'session'):
        request.session[poll.get_cookie_name()] = 1