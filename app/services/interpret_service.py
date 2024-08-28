from typing import Any, Union, List

from croniter import croniter, CroniterBadCronError
from cron_descriptor import CasingTypeEnum, ExpressionDescriptor
from datetime import datetime


def convert_special_schedules(expression: str) -> str:
    special_schedules = {
        "@yearly": "0 0 1 1 *",
        "@annually": "0 0 1 1 *",
        "@monthly": "0 0 1 * *",
        "@weekly": "0 0 * * 0",
        "@daily": "0 0 * * *",
        "@midnight": "0 0 * * *",
        "@hourly": "0 * * * *",
    }
    return special_schedules.get(expression, expression)


def interpret_cron_expression(expression: str) -> Union[str, dict[str, List[Any]] | str]:
    now = datetime.now()

    expression = convert_special_schedules(expression)
    cron = validate_cron_expression(expression, now)
    if not cron:
        raise ValueError("Invalid cron expression.")

    # Example: Next 5 occurrences of the cron job
    next_occurrences = [cron.get_next(datetime).strftime('%Y-%m-%d %H:%M:%S') for _ in range(5)]

    cron_parts = expression.split()
    detailed_description = {
        "minutes": cron_parts[0],
        "hours": cron_parts[1],
        "day_of_month": cron_parts[2],
        "month": cron_parts[3],
        "day_of_week": cron_parts[4]
    }
    return {
        "expression": expression,
        "valid": True,
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "next_occurrences": next_occurrences,
        "interpreted_meaning": cron_to_human(expression),
        "detailed_description": detailed_description,
        "warnings": check_for_edge_cases(expression)
    }


def validate_cron_expression(expression: str, now: datetime) -> Union[None, croniter]:
    try:
        return croniter(expression, now)
    except (ValueError, KeyError, CroniterBadCronError):
        return None


def cron_to_human(expression: str) -> str:
    descriptor = ExpressionDescriptor(
        expression=expression,
        casing_type = CasingTypeEnum.Sentence,
        # use_24hour_time_format = True
    )
    return descriptor.get_description()

def check_for_edge_cases(expression: str) -> List[str]:
    """Checks for edge cases"""
    warnings = []

    if expression.startswith("0 0 29 2"):
        warnings.append("This cron expression will only run on leap years.")
    if "*/" in expression:
        warnings.append("This cron expression uses intervals, which may lead to unexpected timings.")
    return warnings
