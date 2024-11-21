# -*- coding: utf-8 -*-
from zope import schema
from zope.interface import Interface
from zope.annotation.interfaces import IAnnotations
from plone.indexer import indexer
from plone.dexterity.interfaces import IDexterityContent
from zope.component import adapts
from zope.interface import implementer

from ushare.core import _

NEWS_IN_APP_KEY = 'ushare.core.show_new_in_app'  # TODO ushare..core.show_new_in_app


class IShowInApp(Interface):
    """ An object which can be marked as inapp
    """

    is_inapp = schema.Bool(
        title=_(u"Tells if an object is shown in App"),
        default=False
    )


@implementer(IShowInApp)
class ShowInAppMarker(object):
    """ Adapts all non folderish AT objects (IBaseContent) to have
        the inapp attribute (Boolean) as an annotation.
        It is available through Iinapp adapter.
    """
    adapts(Interface)

    def __init__(self, context):
        self.context = context

        annotations = IAnnotations(context)
        self._is_inapp = annotations.setdefault(NEWS_IN_APP_KEY, False)

    def get_inapp(self):
        annotations = IAnnotations(self.context)
        self._is_inapp = annotations.setdefault(NEWS_IN_APP_KEY, '')
        return self._is_inapp

    def set_inapp(self, value):
        annotations = IAnnotations(self.context)
        annotations[NEWS_IN_APP_KEY] = value
        self.context.reindexObject(idxs=["is_inapp"])

    is_inapp = property(get_inapp, set_inapp)


@indexer(IDexterityContent)
def showinappIndexer(context):
    """Create a catalogue indexer, registered as an adapter for DX content. """
    return IShowInApp(context).is_inapp
