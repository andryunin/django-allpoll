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


class ClientTest(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.poll_pk = Poll.objects.order_by('id')[0].pk
        self.vote_url = reverse('allpoll-vote', kwargs={'poll_id': self.poll_pk})

    def testList(self):
        resp = self.client.get(reverse('allpoll-list'))
        self.assertEqual(resp.status_code, 200)

    def testVote(self):
        resp_vote = self.client.get(self.vote_url)
        resp_result = self.client.get(self.vote_url + '?result')

        self.assertEqual(resp_vote.status_code, 200)
        self.assertEqual(resp_result.status_code, 200)
        self.assertNotEqual(resp_vote.content, resp_result.content)


class VoteTest(TestCase):
    fixtures = ['test_data.json']
    urls = 'allpoll.urls'

    USER_NAME = 'testuser'
    USER_PASS = 'testpass'

    def setUp(self):
        self.poll_pk = Poll.objects.order_by('id')[0].pk
        self.url = reverse('allpoll-vote', kwargs={'poll_id': self.poll_pk})
        User.objects.create_user(self.USER_NAME, 't@test.test', self.USER_PASS)
        self._last_ip = 0

    def getData(self):
        poll = Poll.objects.get(id=self.poll_pk)
        choice = poll.choice_set.all()[0]
        data = {'choice_id': choice.id}

        return poll, choice, data

    def getFreeIP(self):
        self._last_ip += 1
        return '127.0.0.%d' % self._last_ip

    def saveCount(self, poll_id, choice_id):
        """Remember current poll and choice counts"""
        self._saved_poll_id = poll_id
        self._saved_choice_id = choice_id
        self._saved_poll_count = Poll.objects.get(id=poll_id).count
        self._saved_choice_count = Choice.objects.get(id=choice_id).count

    def checkCount(self, diff):
        """Check diff between saved and current poll and choice counts"""
        poll = Poll.objects.get(id=self._saved_poll_id)
        choice = Choice.objects.get(id=self._saved_choice_id)

        if self._saved_poll_count + diff != poll.count:
            return False
        if self._saved_choice_count + diff != choice.count:
            return False

        return True

    def testAjax(self):
        client = Client()
        poll, choice, data = self.getData()
        ip = self.getFreeIP()

        def request():
            return client.post(self.url, data, REMOTE_ADDR=ip,
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.saveCount(poll.id, choice.id)

        self.assertEqual(request().status_code, 200)
        self.assertEqual(request().status_code, 403)

        self.assertTrue(self.checkCount(1))

    def testAnonymous(self):
        client = Client()
        poll = Poll.objects.get(allow_anonymous=False)
        url = reverse('allpoll-vote', kwargs={'poll_id': poll.id})
        choice = poll.choice_set.all()[0]
        data = {'choice_id': choice.id}
        ip = self.getFreeIP()

        def request():
            return client.post(url, data, REMOTE_ADDR=ip)

        self.saveCount(poll.id, choice.id)
        self.assertEqual(request().status_code, 403)
        self.assertTrue(self.checkCount(0))

        client.login(username=self.USER_NAME, password=self.USER_PASS)

        self.saveCount(poll.id, choice.id)
        self.assertEqual(request().status_code, 302)
        self.assertTrue(self.checkCount(1))

    def testCookies(self):
        client = Client()
        poll, choice, data = self.getData()
        ip = self.getFreeIP()

        def request():
            return client.post(self.url, data, REMOTE_ADDR=ip)

        self.saveCount(poll.id, choice.id)

        self.assertEqual(request().status_code, 302)
        self.assertEqual(request().status_code, 403)

        self.assertTrue(self.checkCount(1))


    def testSession(self):
        client = Client()
        poll, choice, data = self.getData()
        ip = self.getFreeIP()

        def request():
            return client.post(self.url, data, REMOTE_ADDR=ip)

        self.saveCount(poll.id, choice.id)

        self.assertEqual(request().status_code, 302)
        del client.cookies[poll.get_cookie_name()]
        self.assertEqual(request().status_code, 403)

        self.assertTrue(self.checkCount(1))

    def testIPLimit(self):
        poll, choice, data = self.getData()
        ip = self.getFreeIP()

        def request():
            client = Client()
            return client.post(self.url, data, REMOTE_ADDR=ip)

        self.saveCount(poll.id, choice.id)
        
        for i in xrange(settings.IP_LIMIT):
            self.assertEqual(request().status_code, 302)
        self.assertEqual(request().status_code, 403)

        self.assertTrue(self.checkCount(settings.IP_LIMIT))

    def testUserLimit(self):
        client = Client()
        client.login(username=self.USER_NAME, password=self.USER_PASS)
        poll, choice, data = self.getData()
        ip = self.getFreeIP()

        def request():
            return client.post(self.url, data, REMOTE_ADDR=ip)

        self.saveCount(poll.id, choice.id)
        
        self.assertEqual(request().status_code, 302)
        self.assertEqual(request().status_code, 403)

        self.assertTrue(self.checkCount(1))