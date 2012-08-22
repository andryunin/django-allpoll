from django.conf import settings

IP_LIMIT = getattr(settings, 'POLLS_IP_LIMIT', 50)