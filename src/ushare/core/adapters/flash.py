# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import INewsItem
from plone.indexer import indexer
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implementer

from ushare.core import _

FLASH_KEY = 'ushare.core.flash'  # TODO ushare..core.flash


class IFlash(Interface):
    """ An object which can be marked as flash
    """

    is_flash = schema.Bool(
        title=_(u"Tells if an object is marked as flash"),
        default=False
    )


@implementer(IFlash)
class FlashMarker(object):
    """ Adapts all non folderish AT objects (IBaseContent) to have
        the flash attribute (Boolean) as an annotation.
        It is available through IFlash adapter.
    """
    adapts(Interface)

    def __init__(self, context):
        self.context = context

        annotations = IAnnotations(context)
        self._is_flash = annotations.setdefault(FLASH_KEY, False)

    def get_flash(self):
        annotations = IAnnotations(self.context)
        self._is_flash = annotations.setdefault(FLASH_KEY, '')
        return self._is_flash

    def set_flash(self, value):
        annotations = IAnnotations(self.context)
        annotations[FLASH_KEY] = value
        self.context.reindexObject(idxs=["is_flash"])

    is_flash = property(get_flash, set_flash)


@indexer(INewsItem)
def flashIndexer(context):
    """Create a catalogue indexer, registered as an adapter for DX content. """
    return IFlash(context).is_flash
