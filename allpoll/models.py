from django.db import models
from django.db import transaction
from django.contrib.auth.models import User


class Poll(models.Model):
    question = models.TextField()
    start_date = models.DateField(null=True)
    stop_date = models.DateField(null=True)
    allow_anonymous = models.BooleanField(default=True)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('-start_date', '-stop_date')
        get_latest_by = 'start_date'

    def __unicode__(self):
        return self.question


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