#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id: mixins.py 96794 2016-09-14 20:01:39Z carlos.sanchez $
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import time

from zope import interface

from zope.event import notify

from nti.publishing.interfaces import IPublishable
from nti.publishing.interfaces import IDefaultPublished
from nti.publishing.interfaces import ICalendarPublishable

from nti.publishing.interfaces import ObjectPublishedEvent
from nti.publishing.interfaces import ObjectUnpublishedEvent
from nti.publishing.interfaces import CalendarPublishableModifiedEvent

from nti.publishing.utils import is_published
from nti.publishing.utils import is_calendar_published


@interface.implementer(IPublishable)
class PublishableMixin(object):

    publishLastModified = None

    __publication_predicate_interface__ = None

    def __init__(self, *args, **kwargs):
        super(PublishableMixin, self).__init__(*args, **kwargs)

    def update_publish_last_mod(self):
        """
        Update the publish last modification time.
        """
        self.publishLastModified = time.time()
    updatePublishLastModified = _update_publish_last_mod = update_publish_last_mod

    def do_publish(self, event=True, **kwargs):
        interface.alsoProvides(self, IDefaultPublished)
        if event:
            notify(ObjectPublishedEvent(self))
        self.update_publish_last_mod()

    def publish(self, *args, **kwargs):
        if not self.is_published():
            self.do_publish(**kwargs)

    def do_unpublish(self, event=True, **kwargs):
        interface.noLongerProvides(self, IDefaultPublished)
        if event:
            notify(ObjectUnpublishedEvent(self))
        self.update_publish_last_mod()

    def unpublish(self, *args, **kwargs):
        if self.is_published():
            self.do_unpublish(**kwargs)

    def is_published(self, *args, **kwargs):
        interface =  kwargs.get('interface', None) \
                  or getattr(self, '__publication_predicate_interface__', None)
        if interface is not None:
            kwargs['interface'] = interface
        return is_published(self, *args, **kwargs)
    isPublished = is_published


@interface.implementer(ICalendarPublishable)
class CalendarPublishableMixin(PublishableMixin):

    publishEnding = None
    publishBeginning = None

    def publish(self, start=None, end=None, **kwargs):
        if start is None:
            # Explicit publish, reset any dates we have.
            # The user may publish but specify just an end date.
            self.do_publish(**kwargs)
        else:
            notify(CalendarPublishableModifiedEvent(self, start, end))
            interface.noLongerProvides(self, IDefaultPublished)
            # Update mod time and notify our object is changing.
            self.update_publish_last_mod()
        self.publishEnding = end
        self.publishBeginning = start

    def unpublish(self, *args, **kwargs):
        self.do_unpublish(**kwargs)
        self.publishEnding = None
        self.publishBeginning = None

    def is_published(self, *args, **kwargs):
        interface = kwargs.get('interface', None) \
                 or getattr(self, '__publication_predicate_interface__', None)
        if interface is not None:
            kwargs['interface'] = interface
        return is_calendar_published(self, *args, **kwargs)
    isPublished = is_published
