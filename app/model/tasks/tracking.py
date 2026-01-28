import tempfile
from datetime import datetime, UTC

import sqlalchemy as sql
from sqlalchemy.orm.attributes import flag_modified
from celery import shared_task
from celery.utils.log import get_task_logger

from db import FLASK_DB
from app.model.orm import (
    PageVisit,
    PageVisitCounter,
)

_LOGGER = get_task_logger(__name__)


@shared_task
def aggregate_page_visits():
    db_session = FLASK_DB.session

    _aggregate_page_visits(db_session)


def _aggregate_page_visits(db_session):
    _LOGGER.info(f"Page visit aggregation start")

    start_time, end_time, last_id = db_session.execute(
        sql.select(
            sql.func.min(PageVisit.createdAt),
            sql.func.max(PageVisit.createdAt),
            sql.func.max(PageVisit.id),
        )
    ).one()

    _LOGGER.info(f"Recording page visits from {start_time} to {end_time}")

    total_count           = 0
    total_visit_count     = 0
    total_bot_visit_count = 0
    total_visitors        = set()
    total_users           = set()

    paths     = {}
    countries = {}

    page_visits = db_session.scalars(sql.select(PageVisit).where(PageVisit.id <= last_id))

    for pv in page_visits:
        total_count += 1

        pv_path = pv.path
        if pv_path not in paths:
            paths[pv_path] = {
                'visitCount': 0,
                'botVisitCount': 0,
                'visitors': set(),
                'users': set(),
            }

        pv_country = pv.country or "Unknown"
        if pv_country not in countries:
            countries[pv_country] = {
                'visitCount': 0,
                'botVisitCount': 0,
                'visitors': set(),
                'users': set(),
            }

        if pv.isBot:
            paths[pv_path]['botVisitCount'] += 1
            countries[pv_country]['botVisitCount'] += 1
            total_bot_visit_count += 1
        else:
            paths[pv_path]['visitCount'] += 1
            countries[pv_country]['visitCount'] += 1
            total_visit_count += 1

            paths[pv_path]['visitors'].add(pv.uuid)
            countries[pv_country]['visitors'].add(pv.uuid)
            total_visitors.add(pv.uuid)

            if pv.isUser:
                paths[pv_path]['users'].add(pv.uuid)
                countries[pv_country]['users'].add(pv.uuid)
                total_users.add(pv.uuid)

    for entry in [*paths.values(), *countries.values()]:
        entry['visitorCount'] = len(entry['visitors'])
        entry['userCount']    = len(entry['users'])

        del entry['visitors']
        del entry['users']

    pvc = PageVisitCounter(
        startTimestamp=start_time,
        endTimestamp=end_time,
        paths=paths,
        countries=countries,
        totalVisitCount=total_visit_count,
        totalBotVisitCount=total_bot_visit_count,
        totalVisitorCount=len(total_visitors),
        totalUserCount=len(total_users),
    )
    db_session.add(pvc)
    db_session.commit()

    _LOGGER.info(f"Recorded {total_count} page visits")

    # Clean up processed page views:
    db_session.execute(
        sql.delete(PageVisit)
        .where(PageVisit.id <= last_id)
    )
    db_session.commit()
