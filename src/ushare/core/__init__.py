# -*- coding: utf-8 -*-
"""Init and utils."""

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('base')

import pkg_resources


try:
    pkg_resources.get_distribution('upcnet.cas')
except pkg_resources.DistributionNotFound:
    HAS_CAS = False
else:
    HAS_CAS = True

try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    HAS_DXCT = False
else:
    HAS_DXCT = True

try:
    pkg_resources.get_distribution('plone.app.multilingual')
except pkg_resources.DistributionNotFound:
    HAS_PAM = False
else:
    HAS_PAM = True

try:
    pkg_resources.get_distribution('ulearn5.core')
except pkg_resources.DistributionNotFound:
    IAMULEARN = False
else:
    IAMULEARN = True
