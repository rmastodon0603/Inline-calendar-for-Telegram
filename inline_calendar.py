"""
    Class for creating inline calendar
    Designed as a module for following singleton pattern
    Works with `PyTelegramBotApi <https://github.com/eternnoir/pyTelegramBotAPI>'_
"""
from enum import Enum

from telebot import types
import datetime
from calendar import monthrange


# constants

_INLINE_CALENDAR_NAME = 'inline_calendar'
CALLBACK_WRONG_CHOICE = '{0}_wrong_choice'.format(_INLINE_CALENDAR_NAME)
CALLBACK_PREVIOUS_MONTH = '{0}_previous_month'.format(_INLINE_CALENDAR_NAME)
CALLBACK_NEXT_MONTH = '{0}_next_month'.format(_INLINE_CALENDAR_NAME)

CALLBACK_DAYS = ['{}_day_{}'.format(_INLINE_CALENDAR_NAME, i) for i in range(32)]


# inner vars
_current_date = None
_min_date = None
_max_date = None
_MONTH_NAMES = []
_DAYS_NAMES = []


def _create_header():
    result = []
    if _current_date > _min_date:
        result.append(types.InlineKeyboardButton('<<', callback_data=CALLBACK_PREVIOUS_MONTH))
    else:
        result.append(types.InlineKeyboardButton(' ', callback_data=CALLBACK_WRONG_CHOICE))
    result.append(types.InlineKeyboardButton(_MONTH_NAMES[_current_date.month] + ' ' + str(_current_date.year),
                                             callback_data=CALLBACK_WRONG_CHOICE))
    if _current_date < _max_date:
        result.append(types.InlineKeyboardButton('>>', callback_data=CALLBACK_NEXT_MONTH))
    else:
        result.append(types.InlineKeyboardButton(' ', callback_data=CALLBACK_WRONG_CHOICE))

    return result


def _create_weekdays_buttons():
    return [types.InlineKeyboardButton(_DAYS_NAMES[i], callback_data=CALLBACK_WRONG_CHOICE) for i in range(0, 7)]


def _check_callback(callback):
    if callback == CALLBACK_WRONG_CHOICE:
        return True
    if callback == CALLBACK_NEXT_MONTH or callback == CALLBACK_PREVIOUS_MONTH:
        return True
    if callback in CALLBACK_DAYS:
        return True
    return False


def _inc_month():
    global _current_date
    last_day = _current_date.replace(day=monthrange(_current_date.year, _current_date.month)[1])
    _current_date = last_day+datetime.timedelta(days=1)


def _dec_month():
    global _current_date
    first_day = _current_date.replace(day=1)
    prev_month_lastday = first_day - datetime.timedelta(days=1)
    _current_date = prev_month_lastday.replace(day=1)


def init_new(base_date, min_date, max_date, month_names, days_names):
    """
    :param base_date: a datetime object. Day must be equal to 1
    :param min_date: a datetime object. Day must be equal to 1
    :param max_date: a datetime object. Day must be equal to 1
    :param month_names:
    :param days_names:
    :return:
    """
    global _current_date, _min_date, _max_date, _MONTH_NAMES, _DAYS_NAMES
    _current_date = base_date
    _min_date = min_date
    _max_date = max_date
    _MONTH_NAMES = ['-']+month_names
    _DAYS_NAMES = days_names

    _current_date = _current_date.replace(day=1)
    _max_date = _max_date.replace(day=1)
    _min_date = _min_date.replace(day=1)

    if len(_MONTH_NAMES) != 12+1:
        raise Exception('Length of month names is not 12')
    if len(_DAYS_NAMES) != 7:
        raise Exception('Length of days names is not 7')


def delete():
    global _current_date, _min_date, _max_date
    _current_date = _min_date = _max_date = None


def is_inited():
    global _current_date
    return _current_date is not None


def get_keyboard():
    if not is_inited():
        raise Exception('inline_calendar is not inited properly')

    kb = types.InlineKeyboardMarkup()
    kb.row(*_create_header())
    kb.row(*_create_weekdays_buttons())

    f_row = []
    mrange = monthrange(_current_date.year, _current_date.month)
    for i in range(mrange[0]):
        f_row.append(types.InlineKeyboardButton(text=' ', callback_data=CALLBACK_WRONG_CHOICE))

    rows = [f_row]
    for i in range(1, mrange[1] + 1):
        cdate = datetime.date(day=i, month=_current_date.month, year=_current_date.year)
        if cdate.weekday() == 0:
            rows.append([])

        rows[-1].append(types.InlineKeyboardButton(text=i, callback_data=CALLBACK_DAYS[i]))

    cdate = datetime.date(day=mrange[1], month=_current_date.month, year=_current_date.year)

    for i in range(cdate.weekday() + 1, 7):
        rows[-1].append(types.InlineKeyboardButton(text=' ', callback_data=CALLBACK_WRONG_CHOICE))

    for r in rows:
        kb.row(*r)

    return kb


def is_inline_calendar_callbackquery(query):
    return _check_callback(query.data)


class WrongCallbackException(Exception):
    pass


class WrongChoiceCallbackException(Exception):
    pass


def handler_callback(callback):
    if not _check_callback(callback):
        raise WrongCallbackException('Wrong callback is given for handling')

    if callback == CALLBACK_WRONG_CHOICE:
        raise WrongChoiceCallbackException()

    if callback == CALLBACK_PREVIOUS_MONTH:
        _dec_month()
    if callback == CALLBACK_NEXT_MONTH:
        _inc_month()

    if callback in CALLBACK_DAYS:
        return _current_date.replace(day=int(callback.split('_')[-1]))
