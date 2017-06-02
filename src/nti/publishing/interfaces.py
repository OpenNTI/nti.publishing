#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from zope.interface.interfaces import ObjectEvent
from zope.interface.interfaces import IObjectEvent

from zope.lifecycleevent import ObjectModifiedEvent

from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from nti.schema.field import Number
from nti.schema.field import ValidDatetime


class IDefaultPublished(interface.Interface):
    """
    A marker interface mixed in to an instance to specify
    that it has been "published" by its creator, thus sharing
    it with the default sharing applicable to its creator
    (whatever that means).
    """


class IObjectPublishedEvent(IObjectEvent):
    """
    An event that is sent, when an object has been published
    """


class IObjectUnpublishedEvent(IObjectEvent):
    """
    An event that is sent, when an object has been unpublished
    """


@interface.implementer(IObjectPublishedEvent)
class ObjectPublishedEvent(ObjectEvent):
    pass


@interface.implementer(IObjectUnpublishedEvent)
class ObjectUnpublishedEvent(ObjectEvent):
    pass


class IPublishable(interface.Interface):

    publishLastModified = Number(title=u"The timestamp at which this object updated its publication state.",
                                 default=0.0,
                                 required=False)

    def publish(event=True):
        """
        Cause this object to provide :class:`IDefaultPublished`

        :param event: Notify unlock event
        """

    def unpublish(event=True):
        """
        Cause this object to no longer provide :class:`IDefaultPublished`

        :param event: Notify unlock event
        """

    def is_published(*args, **kwargs):
        """
        Return if this object is published
        """
    isPublished = is_published


class ICalendarPublishableMixin(interface.Interface):

    publishBeginning = ValidDatetime(
        title=u"This object is not available before this time",
        description=u"When present, this specifies the time instant at which "
                    u"this obj is to be available.",
        required=False)

    publishEnding = ValidDatetime(
        title=u"This object is not available after this time",
        description=u"When present, this specifies the last instance at which "
                    u"this obj is to be available.",
        required=False)


class ICalendarPublishable(IPublishable, ICalendarPublishableMixin):
    pass


class ICalendarPublishableModifiedEvent(IObjectModifiedEvent, ICalendarPublishableMixin):
    """
    An event that is sent, when an calendar publishable object is modified
    """


@interface.implementer(ICalendarPublishableModifiedEvent)
class CalendarPublishableModifiedEvent(ObjectModifiedEvent):

    def __init__(self, obj, publishBeginning=None, publishEnding=None, *descriptions):
        super(CalendarPublishableModifiedEvent, self).__init__(obj, *descriptions)
        self.publishEnding = publishEnding
        self.publishBeginning = publishBeginning


class INoPublishLink(interface.Interface):
    """
    Marker interface for objects that are publishable but no links to
    publish operations should be provided
    """
INoPublishLink.setTaggedValue('_ext_is_marker_interface', True)


class IPublishablePredicate(interface.Interface):
    """
    Subscriber for publishable objects to determiend if an object
    is published
    """

    def is_published(publishable, principal=None, context=None, *args, **kwargs):
        """
        return if the specified publishable is published for the given
        principal and context
        """
    isPublished = is_published


class ICalendarPublishablePredicate(interface.Interface):
    """
    Subscriber for calendar-publishable objects to determiend if an object
    is published
    """

    def is_published(publishable, principal=None, context=None, *args, **kwargs):
        """
        return if the specified calendar publishable is published for the given
        principal and context
        """
    isPublished = is_published


def get_publishable_predicate(publishable, interface=None):
    interface = IPublishablePredicate if interface is None else interface
    predicates = list(component.subscribers((publishable,), interface))
    def uber_filter(publishable, *args, **kwargs):
        return all((p.is_published(publishable, *args, **kwargs) for p in predicates))
    return uber_filter


def get_calendar_publishable_predicate(publishable, interface=None):
    interface = ICalendarPublishablePredicate if interface is None else interface
    predicates = list(component.subscribers((publishable,), interface))
    def uber_filter(publishable, *args, **kwargs):
        return all((p.is_published(publishable, *args, **kwargs) for p in predicates))
    return uber_filter
