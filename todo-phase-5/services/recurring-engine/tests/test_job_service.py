"""Tests for job_service — cron conversion and job registration."""

from datetime import datetime, timedelta, timezone

import pytest

from app.services.job_service import (
    calculate_reminder_time,
    recurrence_to_cron,
)


class TestRecurrenceToCron:
    def test_daily_interval_1(self):
        result = recurrence_to_cron("daily", interval=1, time_of_day="09:00")
        assert result == "00 09 * * *"

    def test_daily_interval_2(self):
        result = recurrence_to_cron("daily", interval=2, time_of_day="09:00")
        assert result == "@every 48h"

    def test_weekly_with_days(self):
        # days_of_week: 0=Mon, 2=Wed -> cron days: 1,3
        result = recurrence_to_cron("weekly", days_of_week=[0, 2], time_of_day="10:30")
        assert result == "30 10 * * 1,3"

    def test_weekly_default(self):
        result = recurrence_to_cron("weekly", time_of_day="09:00")
        assert result == "00 09 * * 1"

    def test_weekday(self):
        result = recurrence_to_cron("weekday", time_of_day="08:00")
        assert result == "00 08 * * 1-5"

    def test_monthly(self):
        result = recurrence_to_cron("monthly", day_of_month=15, time_of_day="09:00")
        assert result == "00 09 15 * *"

    def test_custom_passthrough(self):
        result = recurrence_to_cron("custom", cron_expression="0 */2 * * *")
        assert result == "0 */2 * * *"


class TestCalculateReminderTime:
    def test_with_due_time(self):
        result = calculate_reminder_time("2030-06-15", "14:00")
        assert result == datetime(2030, 6, 15, 13, 30, tzinfo=timezone.utc)

    def test_without_due_time_defaults_9am(self):
        result = calculate_reminder_time("2030-06-15")
        assert result == datetime(2030, 6, 15, 8, 30, tzinfo=timezone.utc)

    def test_past_reminder_returns_near_future(self):
        # A due time in the past should return a time in the near future
        past_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        result = calculate_reminder_time(past_date, "09:00")
        now = datetime.now(timezone.utc)
        assert result >= now
