from datetime import date

from django.db import models
from django.db.models.query import Q
from django.db import transaction
from django.contrib.auth.models import User


class PollManager(models.Manager):
    def public(self):
        q = Q(start_date__lte=date.today()) | Q(start_date=None)
        return self.filter(q)

    def active(self):
        q_start = Q(start_date__lte=date.today()) | Q(start_date=None)
        q_stop = Q(stop_date__gt=date.today()) | Q(stop_date=None)
        return self.filter(q_start & q_stop)


class Poll(models.Model):
    question = models.TextField()
    start_date = models.DateField(null=True)
    stop_date = models.DateField(null=True)
    allow_anonymous = models.BooleanField(default=True)
    count = models.PositiveIntegerField(default=0)

    objects = PollManager()

    class Meta:
        ordering = ('-start_date', '-stop_date')
        get_latest_by = 'start_date'

    def __unicode__(self):
        return self.question

    def is_voted(self, request):
        return False

    def is_active(self):
        today = date.today()
        return (self.start_date <= today) and (today < stop_date)

    def get_choices(self):
        if not hasattr(self, '_get_choices_cache'):
            self._get_choices_cache = self.choice_set.select_related().all()
        return self._get_choices_cache


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    answer = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('order', 'pk')

    def __unicode__(self):
        return self.answer

    @transaction.commit_on_success
    def vote(self, count=1):
        if count < 0 and -count > self.count:
            raise ValueError("Impossible to deduct too much votes")
        self.poll.count += count
        self.poll.save()
        self.count += count
        self.save()

    def get_percent(self):
        if self.poll.count == 0:
            return 0
        return int((float(self.count) / self.poll.count) * 100)


class Vote(models.Model):
    poll = models.ForeignKey(Poll)
    user = models.ForeignKey(User, null=True)
    ipaddr = models.IPAddressField()
    datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s: %s from %s' % (
            self.datetime.strftime('%Y-%m-%d %H:%M:%S'),
            self.user.username if self.user else '(anonynous)',
            self.ipaddr
        )