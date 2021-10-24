from datetime import datetime, timedelta, date
import heapq
import math
import re
from typing import List

from dateutil.relativedelta import relativedelta
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz
from titlecase import titlecase


def has_fuzzy_match(word: str, sentence: List[str], threshold=80) -> bool:
    s = SequenceMatcher()
    s.set_seq2(word)
    for x in sentence:
        s.set_seq1(x)
        if s.real_quick_ratio() * 100 >= threshold \
                and s.quick_ratio() * 100 >= threshold \
                and s.ratio() * 100 >= threshold:
            return True
    return False


def fuzzy_matches(word: str, sentence: List[str], n=5, threshold=80):
    results = []
    s = SequenceMatcher()
    s.set_seq2(word)
    for i, x in enumerate(sentence):
        s.set_seq1(x)
        if s.real_quick_ratio() * 100 >= threshold and s.quick_ratio() * 100 >= threshold:
            ratio = s.ratio()
            if ratio * 100 >= threshold:
                results.append((ratio * 100, i))

    # Move the best scorers to head of list
    return heapq.nlargest(n, results)


def extract_best_datelike(sentence: List[str], is_title: List[bool]):
    best_event_date = None
    best_date_score = -math.inf
    best_date_sentence_idx = None

    relative_days = {
        'today': 0,
        'day after tomorrow': 2,
        'day after tmrw': 2,
        'tmrw': 1,
        'tomorrow': 1,
    }
    for relative_day, offset in relative_days.items():
        if relative_day.startswith('day'):
            for idx in range(len(sentence) - 2):
                if fuzz.ratio(' '.join(sentence[idx:idx+3]), relative_day) > 80:
                    is_title[idx] = False
                    is_title[idx + 1] = False
                    is_title[idx + 2] = False
                    if idx >= 1 and fuzz.ratio(sentence[idx - 1], 'during') > 80:
                        is_title[idx - 1] = False
                    if idx >= 1 and fuzz.ratio(sentence[idx - 1], 'the') > 60:
                        is_title[idx - 1] = False
                        if idx >= 2 and sentence[idx - 2] in ('on', 'during'):
                            is_title[idx - 2] = False
                    return datetime.today().date() + timedelta(days=offset)
        elif has_fuzzy_match(relative_day, sentence):
            idx = fuzzy_matches(relative_day, sentence)[0][1]
            is_title[idx] = False
            if idx >= 1 and fuzz.ratio(sentence[idx - 1], 'during') > 80:
                is_title[idx - 1] = False
            return datetime.today().date() + timedelta(days=offset)

    months = ('january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
              'november', 'december')
    month_num = datetime.today().month
    month_bonus = 0
    month_idx = None
    for i, month_name in enumerate(months):
        if has_fuzzy_match(month_name, sentence):
            month_num = i + 1
            month_bonus = 100
            month_idx = fuzzy_matches(month_name, sentence)[0][1]
            break
        if month_bonus == 0 and has_fuzzy_match(month_name[:3], sentence):
            month_num = i + 1
            month_bonus = 100
            month_idx = fuzzy_matches(month_name[:3], sentence)[0][1]

    if month_idx is not None:
        is_title[month_idx] = False
    for i in (month_idx - 2, month_idx - 1, month_idx + 1) if month_idx is not None else range(len(sentence)):
        if month_idx is not None and i == month_idx - 2 and sentence[month_idx - 1] != 'of':
            continue
        if i < 0 or i >= len(sentence):
            continue
        word = sentence[i]
        if re.fullmatch('[0-3]?[0-9](st|nd|rd|th)', word) and 1 <= int(word[:-2]) <= 31:
            try:
                day_num = int(word[:-2])
                best_event_date = date(datetime.today().year, month_num, day_num)
                is_title[i] = False
                if month_idx is not None and i == month_idx - 2:
                    is_title[month_idx - 1] = False
                if i >= 1:
                    if sentence[i - 1] == 'on' or fuzz.ratio(sentence[i - 1], 'during') > 80:
                        is_title[i - 1] = False
                    elif i >= 2 and sentence[i - 1] == 'the' and sentence[i - 2] == 'on':
                        is_title[i - 1] = False
                        is_title[i - 2] = False
                if month_idx is not None and month_idx >= 1:
                    if sentence[month_idx - 1] == 'on' or fuzz.ratio(sentence[month_idx - 1], 'during') > 80:
                        is_title[month_idx - 1] = False
                if month_idx is None and best_event_date < datetime.today().date():
                    best_event_date += relativedelta(months=1)
                return best_event_date
            except ValueError:  # invalid date
                continue
        elif word.isdecimal() and 1 <= int(word) <= 31:
            date_score = month_bonus + 50
            day_num = int(word)
            event_date = date(datetime.today().year, month_num, day_num)
            if event_date < datetime.today().date() and month_idx is None:
                date_score -= 1
                event_date += relativedelta(months=1)
            if date_score > best_date_score:
                best_event_date = event_date
                best_date_score = date_score
                best_date_sentence_idx = i

    if best_date_sentence_idx is not None:
        if month_idx is not None and best_date_sentence_idx == month_idx - 2:
            is_title[month_idx - 1] = False
        if best_date_sentence_idx >= 1:
            if sentence[best_date_sentence_idx - 1] == 'on' \
                    or fuzz.ratio(sentence[best_date_sentence_idx - 1], 'during') > 80:
                is_title[best_date_sentence_idx - 1] = False
            elif best_date_sentence_idx >= 2 \
                    and sentence[best_date_sentence_idx - 1] == 'the'\
                    and sentence[best_date_sentence_idx - 2] == 'on':
                is_title[best_date_sentence_idx - 1] = False
                is_title[best_date_sentence_idx - 2] = False
        if month_idx is not None and month_idx >= 1:
            if sentence[month_idx - 1] == 'on' or fuzz.ratio(sentence[month_idx - 1], 'during') > 80:
                is_title[month_idx - 1] = False
        if month_idx is None and best_event_date < datetime.today().date():
            best_event_date += relativedelta(months=1)

    # used_day_of_week = False
    for i, day_of_week in enumerate(('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')):
        if has_fuzzy_match(day_of_week, sentence):
            event_date = datetime.today().date() + timedelta(days=(i - datetime.today().weekday()) % 7)
            date_score, date_sentence_idx = fuzzy_matches(day_of_week, sentence)[0]
            date_score += 25
            if date_score > best_date_score:
                best_event_date = event_date
                best_date_score = date_score
                best_date_sentence_idx = date_sentence_idx
                if best_date_score == 125:
                    # used_day_of_week = True
                    break
        if has_fuzzy_match(day_of_week[:3], sentence, threshold=100):
            event_date = datetime.today().date() + timedelta(days=(i - datetime.today().weekday()) % 7)
            date_score, date_sentence_idx = fuzzy_matches(day_of_week[:3], sentence)[0]
            if date_score > best_date_score:
                best_event_date = event_date
                best_date_score = date_score
                best_date_sentence_idx = date_sentence_idx
                # used_day_of_week = True

    # if used_day_of_week and best_date_sentence_idx >= 1 and sentence[best_date_sentence_idx - 1] == 'next':
    #     best_event_date += timedelta(days=7)

    if best_event_date is None:
        best_event_date = datetime.today().date()
    else:
        is_title[best_date_sentence_idx] = False
        if best_date_sentence_idx >= 1 and sentence[best_date_sentence_idx - 1] in ('on', 'for', 'next', 'the'):
            is_title[best_date_sentence_idx - 1] = False

    return best_event_date


def extract_end_time(sentence: List[str], is_title: List[bool], start_from: int, start_datetime: datetime):
    start_date_datetime = datetime(start_datetime.year, start_datetime.month, start_datetime.day)
    best_idx = None
    ret = None
    for i, word in enumerate(sentence):
        if i < start_from:
            continue
        if i > start_from + 2:
            break
        if re.fullmatch(
            '(0?[0-9]|1[0-2]):[0-5][0-9][ap]m?',
            word
        ):
            hours = int(word.split(':')[0])
            if word.endswith('m'):
                minutes = int(word[-4:-2])
            else:
                minutes = int(word[-3:-1])
            if word.endswith('a') or word.endswith('am'):
                ret = start_date_datetime + timedelta(hours=hours, minutes=minutes)
            else:
                ret = start_date_datetime + timedelta(hours=12 + hours, minutes=minutes)
            best_idx = i
            break
        if re.fullmatch(
            '(0?[0-9]|1[0-2])[ap]m?',
            word
        ):
            hours = int(word[:-2] if word.endswith('m') else word[:-1])
            minutes = 0
            if word.endswith('a') or word.endswith('am'):
                ret = start_date_datetime + timedelta(hours=hours, minutes=minutes)
            else:
                ret = start_date_datetime + timedelta(hours=12 + hours, minutes=minutes)
            best_idx = i
            break
        if re.fullmatch(
            '(0?[0-9]|1[0-9]|2[0-4]):[0-5][0-9]',
            word
        ):
            hours = int(word.split(':')[0])
            minutes = int(word.split(':')[1])
            if hours <= 12 and i + 1 < len(sentence) and sentence[i] in ('am', 'pm'):
                hours += 12
            best_idx = i
            ret = start_date_datetime + timedelta(hours=hours, minutes=minutes)
            break
        if word.isdecimal() and i > 1 and is_title[i - 1] and is_title[i]:
            hours = int(word)
            best_idx = i
            ret = start_date_datetime + timedelta(hours=hours)
            break
    if ret is not None:
        is_title[best_idx] = False
        if best_idx >= 1 and sentence[best_idx - 1] in ('from', 'at', 'to'):
            is_title[best_idx - 1] = False
        return ret
    return None
   

def extract_best_datetime_duration(sentence: List[str], is_title: List[bool]):
    event_date = extract_best_datelike(sentence, is_title)
    event_date = datetime(event_date.year, event_date.month, event_date.day)

    time_names = {
        'morning': 7,
        'noon': 12,
        'afternoon': 15,
        'evening': 18,
        'night': 21,
        'midnight': 24
    }

    best_idx = None
    ret = None
    for i, word in enumerate(sentence):
        done = False
        for time_name, time_name_hours in time_names.items():
            if fuzz.ratio(word, time_name) > 80:
                best_idx = i
                ret = event_date + timedelta(hours=time_name_hours)
                done = True
                break
        if done:
            break
        if re.fullmatch(
            '(0?[0-9]|1[0-2]):[0-5][0-9][ap]m?',
            word
        ):
            hours = int(word.split(':')[0])
            if word.endswith('m'):
                minutes = int(word[-4:-2])
            else:
                minutes = int(word[-3:-1])
            if word.endswith('a') or word.endswith('am'):
                ret = event_date + timedelta(hours=hours, minutes=minutes)
            else:
                ret = event_date + timedelta(hours=12 + hours, minutes=minutes)
            best_idx = i
            break
        if re.fullmatch(
            '(0?[0-9]|1[0-2])[ap]m?',
            word
        ):
            hours = int(word[:-2] if word.endswith('m') else word[:-1])
            minutes = 0
            if word.endswith('a') or word.endswith('am'):
                ret = event_date + timedelta(hours=hours, minutes=minutes)
            else:
                ret = event_date + timedelta(hours=12 + hours, minutes=minutes)
            best_idx = i
            break
        if re.fullmatch(
            '(0?[0-9]|1[0-9]|2[0-4]):[0-5][0-9]',
            word
        ):
            hours = int(word.split(':')[0])
            minutes = int(word.split(':')[1])
            if hours <= 12 and i + 1 < len(sentence) and sentence[i] in ('am', 'pm'):
                hours += 12
            best_idx = i
            ret = event_date + timedelta(hours=hours, minutes=minutes)
            break
        if best_idx is None and word.isdecimal() and i > 1 and is_title[i - 1] and is_title[i]:
            hours = int(word)
            best_idx = i
            ret = event_date + timedelta(hours=hours)
            if i + 1 < len(sentence) and (sentence[i + 1] == 'to' or re.fullmatch('[0-2]?[0-9](:[0-5][0-9])?([ap]m?)?', sentence[i + 1])):
                break
    if ret is not None:
        is_title[best_idx] = False
        if best_idx >= 1 and sentence[best_idx - 1] in ('from', 'at', 'to'):
            is_title[best_idx - 1] = False
        end_time = extract_end_time(sentence, is_title, start_from=best_idx + 1, start_datetime=ret)
        if end_time is None:
            return ret, timedelta(hours=1)
        return ret, end_time - ret
    return None, None


def extract_info(input_string: str):
    sentence = input_string.strip().lower().translate(str.maketrans('', '', ',._;')).split()
    i = 0
    while i < len(sentence):
        if '-' in sentence[i] and all(c.isdecimal() or c in 'apm-:' for c in sentence[i]):
            old = sentence[i]
            sentence[i] = sentence[i].split('-')[0]
            sentence.insert(i + 1, '-'.join(old.split('-')[1:]))
        i += 1

    is_title = [True] * len(sentence)  # 0 title, 1 datetime component

    # date extraction
    start_time, duration = extract_best_datetime_duration(sentence, is_title)

    if start_time is None:
        event_date = extract_best_datelike(sentence, is_title)
        start_time = event_date + timedelta(hours=12)
        duration = timedelta(hours=1)
    elif duration > timedelta(hours=12):
        start_time += timedelta(hours=12)
        duration -= timedelta(hours=12)

    title = ' '.join(titlecase(sentence[i]) for i in range(len(sentence)) if is_title[i])
    return {
        'title': ' '.join(title.split()),
        'startTime': start_time,
        'duration': duration
    }
