# -*- coding: utf-8 -*-
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implementer

ATTRIBUTE_NAME = '_favoritedBy'


class IFavorite(Interface):
    """ Adapt an object to this interface to manage the favorites of an object """

    def get():
        """ Return the usernames who favorited the object. """

    def add(username):
        """ Set the username that favorites the object. """

    def remove(self, username):
        """ Remove the username """


@implementer(IFavorite)
class Favorite(object):
    adapts(Interface)

    def __init__(self, context):
        self.context = context
        self.fans = self.get()
        if not self.fans:
            # Initialize it
            self.fans = set([])
            setattr(self.context, ATTRIBUTE_NAME, self.fans)

    def get(self):
        return getattr(self.context, ATTRIBUTE_NAME, None)

    def add(self, username):
        username = str(username)
        self.fans.add(username)
        setattr(self.context, ATTRIBUTE_NAME, self.fans)
        self.context.reindexObject(idxs=['favoritedBy'])

    def remove(self, username):
        username = str(username)
        if username in self.fans:
            self.fans.remove(username)
            setattr(self.context, ATTRIBUTE_NAME, self.fans)
            self.context.reindexObject(idxs=['favoritedBy'])


@indexer(IDexterityContent)
def favoriteIndexer(context):
    """Create a catalogue indexer, registered as an adapter for DX content. """
    return IFavorite(context).get()
