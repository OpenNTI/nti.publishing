#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

from datetime import datetime

from zope import component
from zope import interface

from nti.publishing.interfaces import IPublishable
from nti.publishing.interfaces import IDefaultPublished
from nti.publishing.interfaces import ICalendarPublishable
from nti.publishing.interfaces import IPublishablePredicate
from nti.publishing.interfaces import ICalendarPublishablePredicate

logger = __import__('logging').getLogger(__name__)


@component.adapter(IPublishable)
@interface.implementer(IPublishablePredicate)
class DefaultPublishablePredicate(object):

    __slots__ = ()

    def __init__(self, *args):
        pass

    def is_published(self, publishable, *unused_args, **unused_kwargs):
        return IDefaultPublished.providedBy(publishable)
    isPublished = is_published


@component.adapter(ICalendarPublishable)
@interface.implementer(ICalendarPublishablePredicate)
class DefaultCalendarPublishablePredicate(object):

    __slots__ = ()

    def __init__(self, *args):
        pass

    def is_published(self, publishable, *unused_args, **unused_kwargs):
        """
        Published if either explicitly published or after
        our start date and before our end date, if provided.
        """
        now = datetime.utcnow()
        end = publishable.publishEnding
        start = publishable.publishBeginning
        result = (   IDefaultPublished.providedBy(publishable)
                  or (start is not None and now > start)) \
            and (end is None or now < end)
        return bool(result)
    isPublished = is_published
