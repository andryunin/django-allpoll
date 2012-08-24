from datetime import date

from django.db import models
from django.db.models.query import Q
from django.db import transaction
from django.contrib.auth.models import User
from django.forms import RadioSelect


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
    count = models.PositiveIntegerField(default=0, editable=False)

    objects = PollManager()

    class Meta:
        ordering = ('-start_date', '-stop_date', '-id')
        get_latest_by = 'start_date'

    def __unicode__(self):
        return self.question

    def is_active(self):
        return self.is_opened and not self.is_closed()

    def is_opened(self):
        if self.start_date != None:
            return self.start_date <= date.today()
        return True

    def is_closed(self):
        if self.stop_date != None:
            return self.stop_date <= date.today()
        return False

    def get_choices(self):
        if not hasattr(self, '_get_choices_cache'):
            self._get_choices_cache = self.choice_set.select_related().all()
        return self._get_choices_cache

    def get_cookie_name(self):
        return 'polls_voted_%s' % self.id

    def get_widget(self):
        choices = [(i.id, i.answer) for i in self.get_choices()]
        return RadioSelect(choices=choices).render(name='choice_id', value="1")


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    answer = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    count = models.PositiveIntegerField(default=0, editable=False)

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

    class Meta:
        unique_together = ('poll', 'user')

    def __unicode__(self):
        return u'%s: %s from %s' % (
            self.datetime.strftime('%Y-%m-%d %H:%M:%S'),
            self.user.username if self.user else '(anonynous)',
            self.ipaddr
        )