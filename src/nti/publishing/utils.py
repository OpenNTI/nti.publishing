#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope.security.interfaces import NoInteraction
from zope.security.management import getInteraction

from zope.security.management import system_user

from nti.publishing.interfaces import get_publishable_predicate
from nti.publishing.interfaces import get_calendar_publishable_predicate


def current_principal(system=True):
    try:
        result = getInteraction().participations[0].principal
    except (NoInteraction, IndexError, AttributeError):
        result = system_user if system else None
    return result
currentPrincipal = current_principal


def is_published(self, interface=None, *args, **kwargs):
    kwargs['principal'] = kwargs.get('principal') or current_principal()
    predicate = get_publishable_predicate(self, interface)
    return predicate(self, *args, **kwargs)
isPublished = is_published


def is_calendar_published(self, interface=None, *args, **kwargs):
    kwargs['principal'] = kwargs.get('principal') or current_principal()
    predicate = get_calendar_publishable_predicate(self, interface)
    return predicate(self, *args, **kwargs)
isCalendarPublished = is_calendar_published
