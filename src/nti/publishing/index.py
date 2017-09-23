#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import time

from zope import component
from zope import interface

from zope.intid.interfaces import IIntIds

from zope.location import locate

from zope.mimetype.interfaces import IContentTypeAware

import BTrees

from nti.publishing.interfaces import IPublishable
from nti.publishing.interfaces import ICalendarPublishable

from nti.zope_catalog.catalog import Catalog

from nti.zope_catalog.datetime import TimestampToNormalized64BitIntNormalizer

from nti.zope_catalog.index import AttributeValueIndex
from nti.zope_catalog.index import NormalizationWrapper
from nti.zope_catalog.index import IntegerValueIndex as RawIntegerValueIndex

from nti.zope_catalog.interfaces import IMetadataCatalog

PUBLISHING_CATALOG_NAME = 'nti.dataserver.++etc++publishing-catalog'

#: Published object MimeType
IX_MIMETYPE = 'mimeType'

#: Publish flag
IX_PUBLISHED = 'published'

#: Publish Ending
IX_PUBLISH_ENDING = 'publishEnding'

#: Publish Beginning
IX_PUBLISH_BEGINNING = 'publishBeginning'

#: Calendar publishable index
IX_CALENDAR_PUBLISHABLE = 'calendarPublishable'

#: Transaction time
IX_PUBLISH_LAST_MODIFIED = 'publishLastModified'

logger = __import__('logging').getLogger(__name__)


class PublishLastModifiedRawIndex(RawIntegerValueIndex):
    pass


def PublishLastModifiedIndex(family=BTrees.family64):
    return NormalizationWrapper(field_name=IX_PUBLISH_LAST_MODIFIED,
                                interface=IPublishable,
                                index=PublishLastModifiedRawIndex(family=family),
                                normalizer=TimestampToNormalized64BitIntNormalizer())


class ValidatingPublishBeginning(object):

    __slots__ = (IX_PUBLISH_BEGINNING,)

    def __init__(self, obj, unused_default):
        if      ICalendarPublishable.providedBy(obj) \
            and obj.publishBeginning is not None:
            ts = time.mktime(obj.publishBeginning.timetuple())
            self.publishBeginning = ts

    def __reduce__(self):
        raise TypeError()


class PublishBeginningRawIndex(RawIntegerValueIndex):
    pass


def PublishBeginningIndex(family=BTrees.family64):
    return NormalizationWrapper(field_name=IX_PUBLISH_BEGINNING,
                                interface=ValidatingPublishBeginning,
                                index=PublishBeginningRawIndex(family=family),
                                normalizer=TimestampToNormalized64BitIntNormalizer())


class ValidatingPublishEnding(object):

    __slots__ = (IX_PUBLISH_ENDING,)

    def __init__(self, obj, unused_default):
        if      ICalendarPublishable.providedBy(obj) \
            and obj.publishEnding is not None:
            ts = time.mktime(obj.publishEnding.timetuple())
            self.publishEnding = ts

    def __reduce__(self):
        raise TypeError()


class PublishEndingRawIndex(RawIntegerValueIndex):
    pass


def PublishEndingIndex(family=BTrees.family64):
    return NormalizationWrapper(field_name=IX_PUBLISH_ENDING,
                                interface=ValidatingPublishEnding,
                                index=PublishEndingRawIndex(family=family),
                                normalizer=TimestampToNormalized64BitIntNormalizer())


class ValidatingMimeType(object):

    __slots__ = (IX_MIMETYPE,)

    def __init__(self, obj, unused_default):
        if IPublishable.providedBy(obj):
            for proxy in (obj, IContentTypeAware(obj, None)):
                mimeType = getattr(proxy, 'mimeType', None) \
                        or getattr(proxy, 'mime_type', None)
                if mimeType:
                    self.mimeType = mimeType
                    break

    def __reduce__(self):
        raise TypeError()


class MimeTypeIndex(AttributeValueIndex):
    default_field_name = IX_MIMETYPE
    default_interface = ValidatingMimeType


class ValidatingCalendarPublishable(object):

    __slots__ = (IX_CALENDAR_PUBLISHABLE,)

    def __init__(self, obj, unused_default):
        if IPublishable.providedBy(obj):
            self.calendarPublishable = ICalendarPublishable.providedBy(obj)

    def __reduce__(self):
        raise TypeError()


class ValidatingPublished(object):

    __slots__ = (IX_PUBLISHED,)

    def __init__(self, obj, unused_default):
        if IPublishable.providedBy(obj):
            self.published = obj.is_published()

    def __reduce__(self):
        raise TypeError()


class PublishedIndex(AttributeValueIndex):
    default_field_name = IX_PUBLISHED
    default_interface = ValidatingPublished


class CalendarPublishableIndex(AttributeValueIndex):
    default_field_name = IX_CALENDAR_PUBLISHABLE
    default_interface = ValidatingCalendarPublishable


@interface.implementer(IMetadataCatalog)
class MetadataPublishingCatalog(Catalog):

    super_index_doc = Catalog.index_doc

    def index_doc(self, docid, ob):
        pass

    def force_index_doc(self, docid, ob):
        self.super_index_doc(docid, ob)


def create_publishing_catalog(catalog=None, family=BTrees.family64):
    if catalog is None:
        catalog = MetadataPublishingCatalog(family=family)
    for name, clazz in ((IX_MIMETYPE, MimeTypeIndex),
                        (IX_PUBLISHED, PublishedIndex),
                        (IX_PUBLISH_ENDING, PublishEndingIndex),
                        (IX_PUBLISH_BEGINNING, PublishBeginningIndex),
                        (IX_CALENDAR_PUBLISHABLE, CalendarPublishableIndex),
                        (IX_PUBLISH_LAST_MODIFIED, PublishLastModifiedIndex)):
        index = clazz(family=family)
        locate(index, catalog, name)
        catalog[name] = index
    return catalog


def get_publishing_catalog(registry=component):
    return registry.queryUtility(IMetadataCatalog, PUBLISHING_CATALOG_NAME)


def install_publishing_catalog(site_manager_container, intids=None):
    lsm = site_manager_container.getSiteManager()
    intids = lsm.getUtility(IIntIds) if intids is None else intids
    catalog = get_publishing_catalog(registry=lsm)
    if catalog is not None:
        return catalog

    catalog = create_publishing_catalog(family=intids.family)
    locate(catalog, site_manager_container, PUBLISHING_CATALOG_NAME)
    intids.register(catalog)
    lsm.registerUtility(catalog,
                        provided=IMetadataCatalog,
                        name=PUBLISHING_CATALOG_NAME)

    for index in catalog.values():
        intids.register(index)
    return catalog
