from datetime import datetime, timedelta, date
import re

from fuzzywuzzy import fuzz


def _extract_date(input_string: str):
    fixed_string = input_string.strip().lower()

    wkday_match = re.search(
        '(^|[^a-z])(mon(day)?|tue(s(day)?)?|wed(nesday)?|thu(r(s(day)?)?)?|fri(day)?|sat(urday)?|sun(day)?)($|[^a-z])',
        fixed_string
    )

    if wkday_match:
        wkday_num = None
        for i, wkday_str in enumerate(('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')):
            if wkday_match[2].startswith(wkday_str):
                wkday_num = i
                break

        for j in range(7):
            test_date = (datetime.today().date() + timedelta(days=j))
            if test_date.weekday() == wkday_num:
                return test_date

    if fuzz.partial_ratio(fixed_string, 'tomorrow') > 80:
        if len(fixed_string) > len('day after tomorrow') - 1 \
                and fuzz.partial_ratio(fixed_string, 'day after tomorrow') > 80:
            return datetime.today().date() + timedelta(days=2)
        else:
            return datetime.today().date() + timedelta(days=1)
    elif fuzz.partial_ratio(fixed_string, 'yesterday') > 80:
        raise ValueError

    return datetime.today().date()


def _extract_time(input_string: str, extracted_date: date):
    fixed_string = input_string.strip().lower()

    time_match = re.search('([01]?[0-9])(:?[0-9]{2})?($|([ap]m?)|[ ?.,:;/_])', fixed_string)
    if time_match:
        hour = int(time_match[1])
        am_pm = time_match[3]
        if am_pm not in ('a', 'am', 'p', 'pm'):
            if 1 <= hour <= 4:  # TODO: make this an adjustable setting
                hour += 12
        elif am_pm.startswith('p'):
            hour += 12

        if time_match[2] is None:
            minute = 0
        else:
            minute = int(time_match[2][-2:])

        candidate_datetime = datetime(
            year=extracted_date.year,
            month=extracted_date.month,
            day=extracted_date.day,
            hour=hour % 24,
            minute=minute
        )
        if hour == 24:
            candidate_datetime += timedelta(days=1)
        if candidate_datetime + timedelta(hours=2) < datetime.today():
            if am_pm in ('a', 'am', 'p', 'pm'):
                candidate_datetime += timedelta(hours=24)
            else:
                candidate_datetime += timedelta(hours=12)

        return candidate_datetime, (time_match.end() if time_match else None)
    else:
        if fuzz.partial_ratio(fixed_string, 'morning') > 80:
            hour, minute = 9, 0
        elif fuzz.partial_ratio(fixed_string, 'afternoon') > 80:
            hour, minute = 15, 0
        elif fuzz.partial_ratio(fixed_string, 'evening') > 80:
            hour, minute = 18, 0
        elif fuzz.partial_ratio(fixed_string, 'night') > 80:
            if len(fixed_string) > len('midnight') and fuzz.partial_ratio(fixed_string, 'midnight') > 80:
                hour, minute = 24, 0
            else:
                hour, minute = 21, 0
        elif fuzz.partial_ratio(fixed_string, 'noon') > 80:
            hour, minute = 12, 0
        else:
            return None, None

        candidate_datetime = datetime(
            year=extracted_date.year,
            month=extracted_date.month,
            day=extracted_date.day,
            hour=hour % 24,
            minute=minute
        )
        if hour == 24:
            candidate_datetime += timedelta(days=1)
        if candidate_datetime + timedelta(hours=8) < datetime.today():
            candidate_datetime += timedelta(days=1)

        return candidate_datetime, None


def extract_start_datetime_and_duration(user_input):
    event_date = _extract_date(user_input)
    event_start_time, time_match_end = _extract_time(user_input, event_date)
    if time_match_end is not None:
        event_end_time = _extract_time(user_input[time_match_end:], event_date)[0]
        if event_end_time is None:
            return event_start_time, timedelta(hours=1)
        if event_end_time < event_start_time:
            event_end_time += timedelta(hours=12)
        if event_end_time < event_start_time:
            raise ValueError('Invalid end time')
    else:
        return event_start_time, timedelta(hours=1)
    return event_start_time, event_end_time - event_start_time


print(extract_start_datetime_and_duration(input()))
