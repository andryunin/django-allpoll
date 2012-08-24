from django.conf import settings

# Allowed votes per one IP
IP_LIMIT = getattr(settings, 'POLLS_IP_LIMIT', 50)

# Polls per page in list view
PAGINATE_BY = getattr(settings, 'POLLS_IP_LIMIT', 10)