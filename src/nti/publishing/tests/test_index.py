#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that
does_not = is_not

import fudge
import pickle
import unittest
from datetime import datetime

from zope import component

import BTrees

from nti.publishing.index import IX_MIMETYPE
from nti.publishing.index import IX_PUBLISHED
from nti.publishing.index import IX_PUBLISH_ENDING
from nti.publishing.index import IX_PUBLISH_BEGINNING
from nti.publishing.index import IX_CALENDAR_PUBLISHABLE
from nti.publishing.index import PUBLISHING_CATALOG_NAME
from nti.publishing.index import IX_PUBLISH_LAST_MODIFIED

from nti.publishing.index import ValidatingMimeType
from nti.publishing.index import ValidatingPublished
from nti.publishing.index import ValidatingPublishEnding
from nti.publishing.index import ValidatingPublishBeginning
from nti.publishing.index import ValidatingCalendarPublishable

from nti.publishing.index import create_publishing_catalog
from nti.publishing.index import install_publishing_catalog

from nti.publishing.index import MetadataPublishingCatalog

from nti.publishing.mixins import CalendarPublishableMixin

from nti.publishing.tests import SharedConfiguringTestLayer

from nti.zope_catalog.interfaces import IDeferredCatalog


class TestIndex(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_pickle(self):
        for factory in (ValidatingCalendarPublishable,
                        ValidatingPublishBeginning, 
                        ValidatingPublishEnding,
                        ValidatingPublished,
                        ValidatingMimeType):
            with self.assertRaises(TypeError):
                pickle.dumps(factory())

    def test_publishable(self):
        publishable = CalendarPublishableMixin()
        publishable.mimeType = 'application/vnd.nextthought.publishable'
        publishable.publishLastModified = 1000.0
        publishable.publishEnding = datetime.fromtimestamp(2000.0)
        publishable.publishBeginning = datetime.fromtimestamp(1500.0)
        # test catalog
        catalog = create_publishing_catalog(family=BTrees.family64)
        assert_that(isinstance(catalog, MetadataPublishingCatalog),
                    is_(True))
        assert_that(catalog, has_length(6))

        # test index
        catalog.force_index_doc(1, publishable)

        index = catalog[IX_MIMETYPE]
        assert_that(index.documents_to_values,
                    has_entry(1, is_('application/vnd.nextthought.publishable')))

        index = catalog[IX_PUBLISHED]
        assert_that(index.documents_to_values,
                    has_entry(1, is_(False)))

        index = catalog[IX_CALENDAR_PUBLISHABLE]
        assert_that(index.documents_to_values,
                    has_entry(1, is_(True)))

        index = catalog[IX_PUBLISH_LAST_MODIFIED]
        assert_that(index.index.documents_to_values,
                    has_entry(1, is_(4651655465120301056)))

        index = catalog[IX_PUBLISH_BEGINNING]
        assert_that(index.index.documents_to_values,
                    has_entry(1, is_(4654311885213007872)))

        index = catalog[IX_PUBLISH_ENDING]
        assert_that(index.index.documents_to_values,
                    has_entry(1, is_(4656422947538337792)))
        
    def test_install_publishing_catalog(self):
        intids = fudge.Fake().provides('register').has_attr(family=BTrees.family64)
        catalog = install_publishing_catalog(component, intids)
        assert_that(catalog, is_not(none()))
        assert_that(install_publishing_catalog(component, intids),
                    is_(catalog))
        component.getGlobalSiteManager().unregisterUtility(catalog, IDeferredCatalog,
                                                           PUBLISHING_CATALOG_NAME)
