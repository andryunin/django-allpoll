from django.test import TestCase

from allpoll.models import Poll, Choice, Vote


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