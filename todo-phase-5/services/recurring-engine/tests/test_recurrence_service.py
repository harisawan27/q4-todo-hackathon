"""Tests for recurrence_service — pure logic, no mocking needed."""

from datetime import date, timedelta

import pytest

from app.models.recurrence import RecurrenceEndCondition, RecurrenceFrequency, RecurrenceRule
from app.services.recurrence_service import (
    _next_daily,
    _next_from_cron,
    _next_monthly,
    _next_weekday,
    _next_weekly,
    calculate_next_occurrence,
    validate_recurrence_rule,
)


class TestNextDaily:
    def test_interval_1(self):
        result = _next_daily(date(2025, 1, 1), 1)
        assert result == date(2025, 1, 2)

    def test_interval_3(self):
        result = _next_daily(date(2025, 1, 1), 3)
        assert result == date(2025, 1, 4)

    def test_across_month_boundary(self):
        result = _next_daily(date(2025, 1, 31), 1)
        assert result == date(2025, 2, 1)


class TestNextWeekly:
    def test_next_monday(self):
        # 2025-01-06 is a Monday
        result = _next_weekly(date(2025, 1, 6), 1, [0])  # 0=Monday
        assert result.weekday() == 0
        assert result > date(2025, 1, 6)

    def test_multiple_days(self):
        # Should land on either Mon(0) or Wed(2)
        result = _next_weekly(date(2025, 1, 6), 1, [0, 2])
        assert result.weekday() in [0, 2]
        assert result > date(2025, 1, 6)


class TestNextWeekday:
    def test_from_friday(self):
        # 2025-01-03 is Friday
        result = _next_weekday(date(2025, 1, 3))
        assert result == date(2025, 1, 6)  # Monday

    def test_from_saturday(self):
        result = _next_weekday(date(2025, 1, 4))
        assert result == date(2025, 1, 6)  # Monday

    def test_from_wednesday(self):
        result = _next_weekday(date(2025, 1, 1))  # Wed
        assert result == date(2025, 1, 2)  # Thu


class TestNextMonthly:
    def test_same_day(self):
        result = _next_monthly(date(2025, 1, 15), 1, 15)
        assert result == date(2025, 2, 15)

    def test_interval_2(self):
        result = _next_monthly(date(2025, 1, 15), 2, 15)
        assert result == date(2025, 3, 15)

    def test_day_clamped_to_28(self):
        result = _next_monthly(date(2025, 1, 15), 1, 31)
        # day_of_month > 28 gets clamped
        assert result.day == 28


class TestNextFromCron:
    def test_daily_9am(self):
        # croniter from midnight Jan 1 fires at 9am same day
        result = _next_from_cron("0 9 * * *", date(2025, 1, 1))
        assert result == date(2025, 1, 1)

    def test_every_monday(self):
        result = _next_from_cron("0 9 * * 1", date(2025, 1, 6))  # Mon
        assert result.weekday() == 0  # Monday


class TestCalculateNextOccurrence:
    def test_inactive_rule_returns_none(self):
        rule = RecurrenceRule(
            task_id="t1", user_id="u1",
            frequency=RecurrenceFrequency.DAILY,
            is_active=False,
        )
        assert calculate_next_occurrence(rule) is None

    def test_count_exhausted_returns_none(self):
        rule = RecurrenceRule(
            task_id="t1", user_id="u1",
            frequency=RecurrenceFrequency.DAILY,
            end_condition=RecurrenceEndCondition.COUNT,
            end_count=5,
            instances_generated=5,
        )
        assert calculate_next_occurrence(rule) is None

    def test_end_date_passed_returns_none(self):
        rule = RecurrenceRule(
            task_id="t1", user_id="u1",
            frequency=RecurrenceFrequency.DAILY,
            end_condition=RecurrenceEndCondition.DATE,
            end_date=date(2020, 1, 1),
        )
        assert calculate_next_occurrence(rule) is None

    def test_daily_returns_future_date(self):
        future = date.today() + timedelta(days=10)
        rule = RecurrenceRule(
            task_id="t1", user_id="u1",
            frequency=RecurrenceFrequency.DAILY,
        )
        result = calculate_next_occurrence(rule, after=future)
        assert result is not None
        assert result > future

    def test_custom_cron(self):
        future = date.today() + timedelta(days=10)
        rule = RecurrenceRule(
            task_id="t1", user_id="u1",
            frequency=RecurrenceFrequency.CUSTOM,
            cron_expression="0 9 * * *",
        )
        result = calculate_next_occurrence(rule, after=future)
        assert result is not None
        assert result >= future


class TestValidateRecurrenceRule:
    def test_weekly_without_days(self):
        errors = validate_recurrence_rule({"frequency": "weekly"})
        assert any("days_of_week" in e for e in errors)

    def test_monthly_day_over_28(self):
        errors = validate_recurrence_rule({"frequency": "monthly", "day_of_month": 31})
        assert any("day_of_month" in e for e in errors)

    def test_custom_without_cron(self):
        errors = validate_recurrence_rule({"frequency": "custom"})
        assert any("cron_expression" in e for e in errors)

    def test_invalid_cron_expression(self):
        errors = validate_recurrence_rule({"frequency": "custom", "cron_expression": "not-a-cron"})
        assert any("Invalid cron" in e for e in errors)

    def test_valid_daily(self):
        errors = validate_recurrence_rule({"frequency": "daily"})
        assert errors == []
