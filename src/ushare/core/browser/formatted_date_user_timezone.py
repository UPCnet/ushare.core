# -*- coding: utf-8 -*-
from Acquisition import Explicit
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from datetime import datetime
from plone import api
from plone.app.event.base import DT
from plone.app.event.base import ulocalized_time
from plone.event.interfaces import IEventAccessor
from plone.event.utils import is_same_day
from plone.event.utils import is_same_time

from ushare.core.utils import getUserPytzTimezone


class FormattedDateUserTimezoneProvider(Explicit):
    template = ViewPageTemplateFile(u'formatted_date.pt')

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.context = context
        self.request = request

    def __call__(self, occ):
        """Return a formatted date string.

        :param occ: An event or occurrence.
        :type occ: IEvent, IOccurrence or IEventAccessor ushare. object
        :returns: Formatted date string for display.
        :rtype: string

        """
        self.date_dict = dates_for_display_user_timezone(occ)
        if self.date_dict is None:
            # Don't break for potential Events without start/end.
            return u""
        return self.template(self)


def dates_for_display_user_timezone(occurrence):
    """ Return a dictionary containing pre-calculated information for building
    <start>-<end> date strings.

    Keys are:
        'start_date' - date string of the start date
        'start_time' - time string of the start date
        'end_date'   - date string of the end date
        'end_time'   - time string of the end date
        'start_iso'  - start date in iso format
        'end_iso'    - end date in iso format
        'same_day'   - event ends on the same day
        'same_time'  - event ends at same time
        'whole_day'  - whole day events
        'open_end'   - events without end time

    :param occurrence: Event or occurrence object.
    :type occurrence: IEvent, IOccurrence or IEventAccessor ushare. object.
    :returns: Dictionary with date strings.
    :rtype: dict


    The behavior os ulocalized_time() with time_only is odd.
    Setting time_only=False should return the date part only and *not*
    the time

    NOTE: these tests are not run, but serve as documentation.
    TODO: remove.
    >>> from DateTime import DateTime
    >>> start = DateTime(2010,3,16,14,40)
    >>> from zope.component.hooks import getSite
    >>> site = getSite()
    >>> ulocalized_time(start, False,  time_only=True, context=site)
    u'14:40'
    >>> ulocalized_time(start, False,  time_only=False, context=site)
    u'14:40'
    >>> ulocalized_time(start, False,  time_only=None, context=site)
    u'16.03.2010'

    """
    if IEventAccessor.providedBy(occurrence):
        acc = occurrence
        occurrence = occurrence.context
    else:
        acc = IEventAccessor(occurrence)

    if acc.start is None or acc.end is None:
        # Eventually optional start/end dates from a potentially Event.
        return None

    timezone = getUserPytzTimezone()

    start = acc.start.astimezone(timezone)
    end = acc.end.astimezone(timezone)

    # this needs to separate date and time as ulocalized_time does
    DT_start = DT(start)
    DT_end = DT(end)

    current_user = api.user.get_current()
    try:
        format_time = current_user.getProperty('format_time')
    except:
        format_time = ''

    start_date = ulocalized_time(
        DT_start, long_format=False, time_only=None, context=occurrence
    )
    start_time = ulocalized_time(
        DT_start, long_format=False, time_only=True, context=occurrence
    )
    end_date = ulocalized_time(
        DT_end, long_format=False, time_only=None, context=occurrence
    )
    end_time = ulocalized_time(
        DT_end, long_format=False, time_only=True, context=occurrence
    )

    same_day = is_same_day(start, end)
    same_time = is_same_time(start, end)

    # set time fields to None for whole day events
    if acc.whole_day:
        start_time = end_time = None
    if acc.open_end:
        end_time = None

    start_iso = acc.whole_day and start.date().isoformat()\
        or start.isoformat()
    end_iso = acc.whole_day and end.date().isoformat()\
        or end.isoformat()

    if format_time != None and format_time != '':
        if start_time != None:
            if 'PM' in start_time or 'AM' in start_time or 'pm' in start_time or 'am' in start_time:
                DT_start_time = datetime.strptime(str(start_time), '%I:%M %p')
            else:
                DT_start_time = datetime.strptime(str(start_time), '%H:%M')

            if 'hh:i A' in format_time:
                start_time = DT_start_time.strftime('%I:%M %p')
            else:
                start_time = DT_start_time.strftime('%H:%M')

        if end_time != None:
            if 'PM' in end_time or 'AM' in end_time or 'pm' in end_time or 'am' in end_time:
                DT_end_time = datetime.strptime(str(end_time), '%I:%M %p')
            else:
                DT_end_time = datetime.strptime(str(end_time), '%H:%M')

            if 'hh:i A' in format_time:
                end_time = DT_end_time.strftime('%I:%M %p')
            else:
                end_time = DT_end_time.strftime('%H:%M')

    return dict(
        # Start
        start_date=start_date,
        start_time=start_time,
        start_iso=start_iso,

        # End
        end_date=end_date,
        end_time=end_time,
        end_iso=end_iso,

        # Meta
        same_day=same_day,
        same_time=same_time,
        whole_day=acc.whole_day,
        open_end=acc.open_end,
    )
