# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import INewsItem
from plone.indexer import indexer
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implementer

from ushare.core import _

OUTOFLIST_KEY = 'ushare.core.outoflist'  # TODO ushare..core.outoflist


class IOutOfList(Interface):
    """ An object which can be marked as outoflist
    """

    is_outoflist = schema.Bool(
        title=_(u"Tells if an object is marked as outoflist"),
        default=False
    )


@implementer(IOutOfList)
class OutOfListMarker(object):
    """ Adapts all non folderish AT objects (IBaseContent) to have
        the outoflist attribute (Boolean) as an annotation.
        It is available through IOutOfList adapter.
    """
    adapts(Interface)

    def __init__(self, context):
        self.context = context

        annotations = IAnnotations(context)
        self._is_outoflist = annotations.setdefault(OUTOFLIST_KEY, False)

    def get_outoflist(self):
        annotations = IAnnotations(self.context)
        self._is_outoflist = annotations.setdefault(OUTOFLIST_KEY, '')
        return self._is_outoflist

    def set_outoflist(self, value):
        annotations = IAnnotations(self.context)
        annotations[OUTOFLIST_KEY] = value
        self.context.reindexObject(idxs=["is_outoflist"])

    is_outoflist = property(get_outoflist, set_outoflist)


@indexer(INewsItem)
def outoflistIndexer(context):
    """Create a catalogue indexer, registered as an adapter for DX content. """
    return IOutOfList(context).is_outoflist
