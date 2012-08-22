from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from allpoll.models import Poll, Choice, Vote
from allpoll import settings


class CounterTest(TestCase):
    fixtures = ['test_data.json']

    def testCounter(self):
        poll = Poll.objects.order_by('pk')[0]
        choice = poll.choice_set.all()

        choice[0].vote()
        choice[1].vote(10)
        choice[1].vote(-5)

        poll = Poll.objects.order_by('pk')[0]

        self.assertEqual(choice[0].count, 1)
        self.assertEqual(choice[1].count, 5)
        self.assertEqual(poll.count, 6)


class VoteTest(TestCase):
    fixtures = ['test_data.json']
    urls = 'allpoll.urls'

    USER_NAME = 'testuser'
    USER_PASS = 'testpass'

    def setUp(self):
        self.poll_pk = Poll.objects.order_by('id')[0].pk
        self.url = reverse('vote', kwargs={'poll_id': self.poll_pk})
        User.objects.create_user(self.USER_NAME, 't@test.test', self.USER_PASS)

    def testIPLimit(self):
        choice = Poll.objects.get(id=self.poll_pk).choice_set.all()[0]
        data = {'choice_id': choice.id}
        poll_count_start = Poll.objects.get(id=self.poll_pk).count

        def request():
            client = Client()
            return client.post(self.url, data, REMOTE_ADDR='127.0.0.1')

        for i in xrange(settings.IP_LIMIT):
            self.assertEqual(request().status_code, 200)
        
        poll = Poll.objects.get(id=self.poll_pk)
        self.assertEqual(poll.count - poll_count_start, settings.IP_LIMIT)

        self.assertEqual(request().status_code, 403)

        poll = Poll.objects.get(id=self.poll_pk)
        self.assertEqual(poll.count - poll_count_start, settings.IP_LIMIT)

    def testUserLimit(self):
        client = Client()
        client.login(username=self.USER_NAME, password=self.USER_PASS)

        choice = Poll.objects.get(id=self.poll_pk).choice_set.all()[0]
        data = {'choice_id': choice.id}
        poll_count_start = Poll.objects.get(id=self.poll_pk).count

        def request():
            return client.post(self.url, data, REMOTE_ADDR='127.0.0.2')

        self.assertEqual(request().status_code, 200)
        self.assertEqual(request().status_code, 403)