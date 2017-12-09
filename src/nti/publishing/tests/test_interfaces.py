#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import has_length
from hamcrest import assert_that

import unittest

from zope import component
from zope import interface

from nti.publishing.interfaces import IPublishables
from nti.publishing.interfaces import get_publishables

from nti.publishing.mixins import PublishableMixin


@interface.implementer(IPublishables)
class FakePublishables(object):

    def iter_objects(self):
        return (PublishableMixin(),)


class TestInterfaces(unittest.TestCase):

    def test_get_recordables(self):
        publishables = FakePublishables()
        component.getGlobalSiteManager().registerUtility(publishables, IPublishables)
        assert_that(list(get_publishables()),
                    has_length(1))
        component.getGlobalSiteManager().unregisterUtility(publishables, IPublishables)
