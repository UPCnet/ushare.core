# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import ILink
from plone.indexer import indexer
from plone.supermodel import model
from zope import schema
from zope.component import adapts
from zope.interface import implements
from zope.interface import alsoProvides

from ushare.core import _


class IOpenLinkInNewWindow(model.Schema):
    """Add open in new window field to link content
    """

    model.order_after(open_link_in_new_window='remoteUrl')
    open_link_in_new_window = schema.Bool(
        title=_(u"open_link_in_new_window"),
        description=_(u"help_open_link_in_new_window"),
        required=False,
        default=False
    )

alsoProvides(IOpenLinkInNewWindow, model.IFormFieldProvider)


class OpenLinkInNewWindow(object):
    implements(IOpenLinkInNewWindow)
    adapts(ILink)

    def __init__(self, context):
        self.context = context

    def _set_open_link_in_new_window(self, value):
        self.context.open_link_in_new_window = value

    def _get_open_link_in_new_window(self):
        return getattr(self.context, 'open_link_in_new_window', None)

    open_link_in_new_window = property(_get_open_link_in_new_window, _set_open_link_in_new_window)


@indexer(ILink)
def open_link_in_new_window(obj):
    return obj.open_link_in_new_window
