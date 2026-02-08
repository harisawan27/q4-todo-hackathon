"""Recurrence rule evaluation and next-instance calculation."""

import logging
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional

from croniter import croniter

from app.models.recurrence import RecurrenceFrequency, RecurrenceRule

logger = logging.getLogger("recurring-engine")


def calculate_next_occurrence(rule: RecurrenceRule, after: date | None = None) -> Optional[date]:
    """Calculate the next occurrence date based on a recurrence rule.

    Args:
        rule: The recurrence rule definition
        after: Calculate next occurrence after this date (defaults to today)

    Returns:
        The next occurrence date, or None if the rule has ended
    """
    if not rule.is_active:
        return None

    base_date = after or date.today()

    # Check end conditions
    if rule.end_condition.value == "count" and rule.end_count:
        if rule.instances_generated >= rule.end_count:
            return None
    if rule.end_condition.value == "date" and rule.end_date:
        if base_date >= rule.end_date:
            return None

    if rule.frequency == RecurrenceFrequency.CUSTOM and rule.cron_expression:
        result = _next_from_cron(rule.cron_expression, base_date)
    elif rule.frequency == RecurrenceFrequency.DAILY:
        result = _next_daily(base_date, rule.interval)
    elif rule.frequency == RecurrenceFrequency.WEEKLY:
        result = _next_weekly(base_date, rule.interval, rule.days_of_week or [0])
    elif rule.frequency == RecurrenceFrequency.WEEKDAY:
        result = _next_weekday(base_date)
    elif rule.frequency == RecurrenceFrequency.MONTHLY:
        result = _next_monthly(base_date, rule.interval, rule.day_of_month or 1)
    else:
        return None

    # Ensure we never generate past-date instances — only future dates (no backfill)
    today = date.today()
    if result and result <= today:
        logger.info(f"Skipping past occurrence {result}, recalculating from today")
        return calculate_next_occurrence(rule, after=today)

    return result


def _next_daily(after: date, interval: int) -> date:
    """Next occurrence for daily frequency."""
    return after + timedelta(days=interval)


def _next_weekly(after: date, interval: int, days_of_week: list[int]) -> date:
    """Next occurrence for weekly frequency. days_of_week: 0=Mon, 6=Sun."""
    current = after + timedelta(days=1)
    weeks_checked = 0
    while weeks_checked < 8 * interval:
        if current.weekday() in days_of_week:
            week_diff = (current - after).days // 7
            if week_diff % interval == 0 or week_diff == 0:
                return current
        current += timedelta(days=1)
        weeks_checked = (current - after).days // 7
    return after + timedelta(weeks=interval)


def _next_weekday(after: date) -> date:
    """Next weekday (Mon-Fri)."""
    current = after + timedelta(days=1)
    while current.weekday() >= 5:  # 5=Sat, 6=Sun
        current += timedelta(days=1)
    return current


def _next_monthly(after: date, interval: int, day_of_month: int) -> date:
    """Next occurrence for monthly frequency."""
    if day_of_month > 28:
        logger.warning(f"day_of_month {day_of_month} > 28, clamping to 28")
        day_of_month = 28

    year = after.year
    month = after.month + interval

    while month > 12:
        month -= 12
        year += 1

    try:
        next_date = date(year, month, day_of_month)
    except ValueError:
        next_date = date(year, month, 28)

    if next_date <= after:
        month += interval
        if month > 12:
            month -= 12
            year += 1
        try:
            next_date = date(year, month, day_of_month)
        except ValueError:
            next_date = date(year, month, 28)

    return next_date


def _next_from_cron(expression: str, after: date) -> date:
    """Next occurrence from a cron expression using croniter."""
    base_dt = datetime.combine(after, time(0, 0), tzinfo=timezone.utc)
    cron = croniter(expression, base_dt)
    next_dt = cron.get_next(datetime)
    return next_dt.date()


def validate_recurrence_rule(rule_data: dict) -> list[str]:
    """Validate a recurrence rule and return any errors."""
    errors = []
    frequency = rule_data.get("frequency")

    if frequency == "weekly" and not rule_data.get("days_of_week"):
        errors.append("days_of_week required for weekly frequency")

    if frequency == "monthly":
        dom = rule_data.get("day_of_month")
        if dom and dom > 28:
            errors.append(f"day_of_month must be 1-28 (got {dom}), per FR-018")

    if frequency == "custom" and not rule_data.get("cron_expression"):
        errors.append("cron_expression required for custom frequency")

    if frequency == "custom" and rule_data.get("cron_expression"):
        try:
            croniter(rule_data["cron_expression"])
        except (ValueError, KeyError):
            errors.append(f"Invalid cron expression: {rule_data['cron_expression']}")

    return errors
