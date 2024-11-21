# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface


class IUshareCoreLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""

class IProtectedContent(Interface):
    """Marker interface for preventing dumb users to delete system configuration
       related content
    """
class INewsFolder(Interface):
    """ Marker interface for the news folders """
