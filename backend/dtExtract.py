from dataclasses import dataclass
from datetime import date, datetime, timedelta
import functools
import re
from typing import List, Any

from dateutil.relativedelta import relativedelta
from fuzzywuzzy import fuzz
import inflect
import numpy as np


@dataclass
class DataSpec:
    data: Any
    mask: np.ndarray
    score: int


def fuzzy_match(a, b, threshold=80):
    return fuzz.ratio(a, b) > threshold


def mask_prepositions(score_bonus=20, additional_prepositions=None):
    prepos = ['a', 'after', 'at', 'by', 'during', 'from', 'in', 'of', 'on', 'the', 'this', 'to']
    if additional_prepositions is not None:
        prepos.extend(additional_prepositions)

    def mask_prepositions_decorator(func):
        @functools.wraps(func)
        def mask_prepositions_wrapper(sentence):
            specs: List[DataSpec] = func(sentence)
            for spec in specs:
                run_length = 0
                for i in range(len(spec.mask) - 2, -1, -1):
                    if spec.mask[i + 1] and any(fuzzy_match(sentence[i], xx) for xx in prepos) and run_length < 5:
                        spec.mask[i] = True
                        spec.score += score_bonus
                        run_length += 1
                    else:
                        run_length = 0
            return specs
        return mask_prepositions_wrapper
    return mask_prepositions_decorator


# TODO: date specs: day of week, relative day, actual date
# TODO: time specs: part of day, time (multiple formats)
@mask_prepositions(score_bonus=20, additional_prepositions=['coming'])
def day_of_week_specs(sentence: List[str]):
    specs = []

    days_of_week = (
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
    )

    def next_week_day(day_of_week: int):
        return datetime.today().date() + timedelta((day_of_week - datetime.today().date().weekday()) % 7)

    for i, day_name in enumerate(days_of_week):
        for j, word in enumerate(sentence):
            if fuzzy_match(word, day_name):
                mask = np.zeros(shape=len(sentence), dtype=bool)
                mask[j] = True
                specs.append(DataSpec(
                    next_week_day(i),
                    mask,
                    100
                ))
            elif fuzzy_match(word, day_name[:3]):
                mask = np.zeros(shape=len(sentence), dtype=bool)
                mask[j] = True
                specs.append(DataSpec(
                    next_week_day(i),
                    mask,
                    75
                ))
    return specs


@mask_prepositions()
def relative_day_specs(sentence: List[str]):
    specs = []

    relative_days = {
        'today': 0,
        'tmrw': 1,
        'tomorrow': 1,
        'day after tmrw': 2,
        'day after tomorrow': 2
    }

    for relative_day, offset in relative_days.items():
        k = len(relative_day.split())
        for i in range(len(sentence) + 1 - k):
            if fuzzy_match(' '.join(sentence[i: i + k]), relative_day):
                mask = np.zeros(shape=len(sentence), dtype=bool)
                for j in range(k):
                    mask[i + j] = True
                specs.append(DataSpec(
                    datetime.today().date() + timedelta(days=offset),
                    mask,
                    score=80 + 10*k,
                ))
    return specs


@mask_prepositions()
def month_specs(sentence: List[str]):
    specs = []

    months = ('january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
              'november', 'december')
    for i in range(12):
        for j, word in enumerate(sentence):
            if fuzzy_match(word, months[i]):
                mask = np.zeros(shape=len(sentence), dtype=bool)
                mask[j] = True
                specs.append(DataSpec(
                    i,
                    mask,
                    100
                ))
            elif fuzzy_match(word, months[i][:3]):
                mask = np.zeros(shape=len(sentence), dtype=bool)
                mask[j] = True
                specs.append(DataSpec(
                    i,
                    mask,
                    75
                ))
    return specs


@mask_prepositions()
def absolute_date_specs(sentence: List[str]):
    specs = []

    p = inflect.engine()
    ordinals = {
        p.ordinal(i): i
        for i in range(1, 32)
    }
    full_ordinals = {
        p.number_to_words(p.ordinal(i)): i
        for i in range(1, 32)
    }
    for month_spec in month_specs(sentence):
        for i, word in enumerate(sentence):
            # Only consider i if it comes directly before or after a month
            if month_spec.mask[i] or (
                not (i + 1 < len(sentence) and month_spec.mask[i + 1])
                and not (i >= 1 and month_spec.mask[i - 1])
            ):
                continue

            if word in full_ordinals:
                day = full_ordinals[word] + 1
                try:
                    new_date = date(year=datetime.today().year, month=1+month_spec.data, day=day)
                except ValueError:
                    continue
                else:
                    if new_date + timedelta(days=100) < datetime.today().date():
                        new_date += relativedelta(years=1)
                    mask = np.zeros(shape=len(sentence), dtype=bool)
                    mask[i] = True
                    specs.append(DataSpec(
                        new_date,
                        mask | month_spec.mask,
                        score=120
                    ))
            elif word in ordinals:
                try:
                    new_date = date(year=datetime.today().year, month=1+month_spec.data, day=ordinals[word])
                except ValueError:
                    continue
                else:
                    if new_date + timedelta(days=100) < datetime.today().date():
                        new_date += relativedelta(years=1)
                    mask = np.zeros(shape=len(sentence), dtype=bool)
                    mask[i] = True
                    specs.append(DataSpec(
                        new_date,
                        mask | month_spec.mask,
                        score=120
                    ))
            elif word.isdecimal() and 1 <= int(word) <= 31:
                try:
                    new_date = date(year=datetime.today().year, month=1+month_spec.data, day=int(word))
                except ValueError:
                    continue
                else:
                    if new_date + timedelta(days=100) < datetime.today().date():
                        new_date += relativedelta(years=1)
                    mask = np.zeros(shape=len(sentence), dtype=bool)
                    mask[i] = True
                    specs.append(DataSpec(
                        new_date,
                        mask | month_spec.mask,
                        score=50
                    ))
            elif all(ord('a') <= ord(c) <= ord('z') for c in word) and 5 <= len(word) <= 15:
                for full_ordinal in full_ordinals:
                    if fuzzy_match(word, full_ordinal):
                        day = full_ordinals[word] + 1
                        try:
                            new_date = date(year=datetime.today().year, month=1 + month_spec.data, day=day)
                        except ValueError:
                            continue
                        else:
                            if new_date + timedelta(days=100) < datetime.today().date():
                                new_date += relativedelta(years=1)
                            mask = np.zeros(shape=len(sentence), dtype=bool)
                            mask[i] = True
                            specs.append(DataSpec(
                                new_date,
                                mask | month_spec.mask,
                                score=100
                            ))
                        break

    for i, word in enumerate(sentence):
        m = re.fullmatch('(2[0-9]{3})[-/]?(0?[1-9]|1[0-2])[-/]?(0?[1-9]|[1-2][0-9]|3[0-1])', word)
        if m:
            try:
                new_date = date(year=int(m[1]), month=int(m[2]), day=int(m[3]))
            except ValueError:
                continue
            else:
                mask = np.zeros(shape=len(sentence), dtype=bool)
                mask[i] = True
                specs.append(DataSpec(
                    new_date,
                    mask,
                    score=200
                ))
        m2 = re.fullmatch('(0?[1-9]|1[0-2])[-/](0?[1-9]|[1-2][0-9]|3[0-1])', word)
        if m2:
            try:
                new_date = date(year=datetime.today().year, month=int(m2[1]), day=int(m2[2]))
            except ValueError:
                continue
            else:
                mask = np.zeros(shape=len(sentence), dtype=bool)
                mask[i] = True
                specs.append(DataSpec(
                    new_date,
                    mask,
                    score=150
                ))

    return specs


@mask_prepositions()
def part_of_day_specs(sentence: List[str]):
    specs = []

    parts_of_day = {
        'morning': 9,
        'noon': 12,
        'afternoon': 15,
        'evening': 18,
        'night': 21,
        'midnight': 24
    }
    for part_of_day, hours in parts_of_day.items():
        for i, word in enumerate(sentence):
            if fuzzy_match(word, part_of_day):
                mask = np.zeros(shape=len(sentence), dtype=bool)
                mask[i] = True
                specs.append(DataSpec(
                    (hours, 0, i),
                    mask,
                    score=80
                ))
    return specs


@mask_prepositions()
def absolute_time_specs(sentence: List[str]):
    specs = []

    for i, word in enumerate(sentence):
        m = re.fullmatch(
            '(0?[0-9]|1[0-9]|2[0-4])(:?[0-5][0-9])?([ap]m)?',
            word
        )
        if not m:
            continue
        score = 10
        hours = int(m[1])
        if m[2] is None:
            minutes = 0
        else:
            if m[2].startswith(':'):
                score += 100
            minutes = int(m[2][-2:])

        mask = np.zeros(shape=len(sentence), dtype=bool)

        am_pm = m[3]
        if am_pm is None and i + 1 < len(sentence):
            if sentence[i + 1] in ('a', 'am'):
                am_pm = 'am'
                mask[i + 1] = True
            elif sentence[i + 1] in ('p', 'pm'):
                am_pm = 'pm'
                mask[i + 1] = True
            elif fuzzy_match(sentence[i + 1], 'oclock'):
                mask[i + 1] = True
        if am_pm is not None:
            score += 200
        if hours <= 5 and am_pm is None:
            hours += 12
        if hours <= 12 and am_pm is not None and am_pm.startswith('p'):
            hours += 12
        mask[i] = True
        specs.append(DataSpec(
            (hours, minutes, i),
            mask=mask,
            score=score
        ))
    return specs


def extract_duration(sentence: List[str]):
    for i in range(len(sentence) - 1):
        if sentence[i] != 'for':
            continue
        if not sentence[i + 1][0].isdecimal():
            continue

        try:
            int(sentence[i + 1])
        except ValueError:
            word = sentence[i + 1]
            num_digits = 1
            for j in range(1, len(word) - 1):
                if word[j].isdecimal():
                    num_digits += 1
                else:
                    break
            if word[num_digits:] in ('s', 'sec', 'secs', 'seconds', 'm', 'min', 'mins', 'minutes', 'h', 'hr', 'hour',
                                     'hours'):
                mask = np.zeros(shape=len(sentence), dtype=bool)
                mask[i:i+2] = True
                if word[num_digits:] in ('s', 'sec', 'secs', 'seconds'):
                    return timedelta(seconds=int(word[:num_digits])), mask
                elif word[num_digits:] in ('m', 'min', 'mins', 'minutes'):
                    return timedelta(minutes=int(word[:num_digits])), mask
                else:
                    return timedelta(hours=int(word[:num_digits])), mask
        else:
            if i + 2 >= len(sentence):
                return None
            elif sentence[i + 2] in ('s', 'sec', 'secs', 'seconds', 'm', 'min', 'mins', 'minutes', 'h', 'hr', 'hour',
                                     'hours'):
                mask = np.zeros(shape=len(sentence), dtype=bool)
                mask[i:i+3] = True
                if sentence[i + 2] in ('s', 'sec', 'secs', 'seconds'):
                    return timedelta(seconds=int(sentence[i + 1])), mask
                elif sentence[i + 2] in ('m', 'min', 'mins', 'minutes'):
                    return timedelta(minutes=int(sentence[i + 1])), mask
                else:
                    return timedelta(hours=int(sentence[i + 1])), mask
    return None, None


def extract_info(user_input: str):
    sentence = user_input.lower().translate(str.maketrans('', '', ',._;')).split()
    i = 0
    while i < len(sentence):
        if '-' in sentence[i] and sentence[i].index('-') not in (0, len(sentence[i]) - 1) \
                and all(c.isdecimal() or c in 'apm-:' for c in sentence[i]):
            old = sentence[i]
            sentence[i] = sentence[i].split('-')[0]
            sentence.insert(i + 1, '-'.join(old.split('-')[1:]))
        i += 1

    event_date_spec_groups = [
        func(sentence)
        for func in (day_of_week_specs, relative_day_specs, absolute_date_specs)
    ]

    event_date_specs = [item for sublist in event_date_spec_groups for item in sublist]
    if len(event_date_specs) == 0:
        event_date = datetime.today().date()
        mask_1 = np.zeros(len(sentence), dtype=bool)
    else:
        best_event_date_spec = max(event_date_specs, key=lambda s: s.score)
        event_date = best_event_date_spec.data
        mask_1 = best_event_date_spec.mask

    time_specs = part_of_day_specs(sentence) + absolute_time_specs(sentence)
    time_scores = np.zeros(len(sentence), dtype=np.uint32)
    specs_by_idx = {spec.data[2]: spec for spec in time_specs}
    for spec in time_specs:
        time_scores[spec.data[2]] += spec.score
    start_hour, start_minute, end_hour, end_minute = None, None, None, None
    start_spec, end_spec = None, None

    if len(time_scores) <= 3:
        best_i = 0
    else:
        best_i = max([i for i in range(len(time_scores) - 3)], key=lambda ii: time_scores[ii:ii+4].sum())

    first = True
    for j in range(4):
        if best_i + j >= len(sentence):
            break
        if sentence[best_i + j] == 'for':
            break
        if time_scores[best_i + j] > 0:
            if first:
                start_hour, start_minute = specs_by_idx[best_i + j].data[:2]
                first = False
                start_spec = specs_by_idx[best_i + j]
            else:

                end_hour, end_minute = specs_by_idx[best_i + j].data[:2]
                end_spec = specs_by_idx[best_i + j]

    duration_mask = None
    if end_hour is None:
        duration, duration_mask = extract_duration(sentence)
        if duration is None:
            duration = timedelta(hours=1)
    else:
        duration = timedelta(hours=(end_hour - start_hour) % 24) + timedelta(minutes=(end_minute - start_minute))
        if duration.total_seconds() >= 12 * 60 * 60:
            if start_hour <= 12 and start_spec.score < 200:
                start_hour += 12
                duration -= timedelta(hours=12)

    if start_hour is None:
        start_hour, start_minute = 12, 0
    elif event_date <= datetime.today().date() and start_hour < datetime.today().hour and start_spec.score < 200:
        start_hour += 12

    final_mask = mask_1
    if start_spec is not None:
        final_mask |= start_spec.mask
    if end_spec is not None:
        final_mask |= end_spec.mask
    if duration_mask is not None:
        final_mask |= duration_mask

    return {
        'title': ' '.join(sentence[i] for i in range(len(sentence)) if ~final_mask[i]),
        'startTime': datetime(event_date.year, event_date.month, event_date.day, start_hour, start_minute),
        'duration': duration
    }
