import tests.init  # noqa: F401

import unittest
from datetime import datetime, timedelta, UTC

import sqlalchemy as sql
from freezegun import freeze_time

from app.model.orm import PageVisit, PageVisitCounter
from app.model.tasks.tracking import _aggregate_page_visits
from tests.database_test import DatabaseTest


class TestTracking(DatabaseTest):
    def test_aggregating_counts(self):
        self.create_page_visit(uuid='p1', path='/')
        self.create_page_visit(uuid='p1', path='/search/')
        self.create_page_visit(uuid='p1', path='/help/')

        self.create_page_visit(uuid='p2', isUser=True, path='/search/')
        self.create_page_visit(uuid='p2', isUser=True, path='/search/', query='?q=foo')
        self.create_page_visit(uuid='p2', isUser=True, path='/search/', query='?q=bar')

        self.create_page_visit(uuid='p3', path='/help/')

        _aggregate_page_visits(self.db_session)

        # We delete all page visits at the end:
        pv_count = self.db_session.scalar(sql.func.count(PageVisit.id))
        self.assertEqual(pv_count, 0)

        # We have created one aggregated counter:
        counter = self.db_session.scalars(sql.select(PageVisitCounter)).one()

        self.assertEqual(counter.counts['/']['visitCount'], 1)
        self.assertEqual(counter.counts['/search/']['visitCount'], 4)
        self.assertEqual(counter.counts['/help/']['visitCount'], 2)

        self.assertEqual(counter.counts['/']['visitorCount'], 1)
        self.assertEqual(counter.counts['/search/']['visitorCount'], 2)
        self.assertEqual(counter.counts['/help/']['visitorCount'], 2)

        self.assertEqual(counter.counts['/']['userCount'], 0)
        self.assertEqual(counter.counts['/search/']['userCount'], 1)
        self.assertEqual(counter.counts['/help/']['userCount'], 0)

    def test_counting_bots(self):
        self.create_page_visit(uuid='p1', path='/', isUser=True)
        self.create_page_visit(uuid='p2', path='/')
        self.create_page_visit(uuid='p3', path='/', isBot=True)
        # Shouldn't happen, but either way shouldn't be counted as a user:
        self.create_page_visit(uuid='p4', path='/', isUser=True, isBot=True)

        _aggregate_page_visits(self.db_session)
        counter = self.db_session.scalars(sql.select(PageVisitCounter)).one()

        self.assertEqual(counter.counts['/']['visitCount'], 2)
        self.assertEqual(counter.counts['/']['botVisitCount'], 2)
        self.assertEqual(counter.counts['/']['visitorCount'], 2)
        self.assertEqual(counter.counts['/']['userCount'], 1)

    def test_recording_timestamps(self):
        with freeze_time(datetime.now(UTC)) as frozen_time:
            self.create_page_visit(uuid='p1', path='/', createdAt=datetime.now(UTC))

            frozen_time.tick(delta=timedelta(seconds=1))
            self.create_page_visit(uuid='p2', isUser=True, path='/', createdAt=datetime.now(UTC))

            frozen_time.tick(delta=timedelta(seconds=5))
            self.create_page_visit(uuid='p3', path='/', createdAt=datetime.now(UTC))

            _aggregate_page_visits(self.db_session)

            # We have created one aggregated counter:
            counter = self.db_session.scalars(sql.select(PageVisitCounter)).one()
            self.assertEqual(counter.endTimestamp - counter.startTimestamp, timedelta(seconds=6))


if __name__ == '__main__':
    unittest.main()
