#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import is_not
from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that
does_not = is_not

import unittest
from datetime import datetime

import BTrees

from nti.publishing.index import IX_MIMETYPE
from nti.publishing.index import IX_PUBLISHED
from nti.publishing.index import IX_PUBLISH_ENDING
from nti.publishing.index import IX_PUBLISH_BEGINNING
from nti.publishing.index import IX_CALENDAR_PUBLISHABLE
from nti.publishing.index import IX_PUBLISH_LAST_MODIFIED

from nti.publishing.index import create_publishing_catalog

from nti.publishing.index import MetadataPublishingCatalog

from nti.publishing.mixins import CalendarPublishableMixin

from nti.publishing.tests import SharedConfiguringTestLayer


class TestIndex(unittest.TestCase):

    layer = SharedConfiguringTestLayer

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
        catalog.super_index_doc(1, publishable)

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
