from django.conf import settings

IP_LIMIT = getattr(settings, 'POLLS_IP_LIMIT', 50)

PAGINATE_BY = getattr(settings, 'POLLS_IP_LIMIT', 1)