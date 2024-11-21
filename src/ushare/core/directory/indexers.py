# -*- coding: utf-8 -*-
from repoze.catalog.catalog import Catalog
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.keyword import CatalogKeywordIndex
from repoze.catalog.indexes.text import CatalogTextIndex
from souper.interfaces import ICatalogFactory
from souper.soup import NodeAttributeIndexer
from zope.interface import implementer

from ushare.core import _


@implementer(ICatalogFactory)
class UserPropertiesSoupCatalogFactory(object):
    """ The local user catalog (LUC) properties index factory. Almost all the
        properties have a field type "FullTextIndex" to allow wildcard queries
        on them. However, the FullTextIndex has a limitation its supported type
        of queries, so for certain operations is needed a FieldIndex for the
        username.

        :index id: FieldIndex - The username id for exact queries
        :index notlegit: FieldIndex - Boolean, if the username is not legit
        :index username: FullTextIndex - The username id for wildcard queries
        :index fullname: FullTextIndex - The user display name
        :index email: FullTextIndex - The user e-mail
        :index location: FullTextIndex - The user location
        :index check_ubicacio: FullTextIndex - Boolean, if the ubicacio is visible for all users
        :index ubicacio: FullTextIndex - The user ubicacio
        :index check_telefon: FullTextIndex - Boolean, if the telefon is visible for all users
        :index telefon: FullTextIndex - The user telephone
        :index check_twitter_username: FullTextIndex - Boolean, if the twitter_username is visible for all userss
        :index twitter_username: FullTextIndex - The user Twitter username

        The properties attribute is used to know in advance which properties are
        listed as 'editable' or user accessible.

        The profile_properties is the list of the user properties displayed on
        the profile page, ordered.

        The public_properties is the list of the profile_properties searchable,
        those that have not been added will be private. If you do not add
        public_properties all the fields will be public.

        The directory_properties is the list of the user properties directory
        properties for display on the directory views, ordered.

        The directory_icons is the dict containing the correspondency with the
        field names and the icon.
    """

    properties = [_(u'username'), _(u'fullname'), _(u'email'), _(u'description'), _(u'location'), _(u'home_page')]
    # public_properties = ['email', 'description', 'location', 'home_page']
    profile_properties = ['email', 'description', 'location', 'home_page']
    directory_properties = ['email', 'location']
    directory_icons = {'email': 'fa fa-envelope', 'location': 'fa fa-building-o'}


    def __call__(self, context):
        catalog = Catalog()
        idindexer = NodeAttributeIndexer('id')
        catalog['id'] = CatalogFieldIndex(idindexer)
        searchable_blob = NodeAttributeIndexer('searchable_text')
        catalog['searchable_text'] = CatalogTextIndex(searchable_blob)
        notlegit = NodeAttributeIndexer('notlegit')
        catalog['notlegit'] = CatalogFieldIndex(notlegit)

        userindexer = NodeAttributeIndexer('username')
        catalog['username'] = CatalogTextIndex(userindexer)
        fullname = NodeAttributeIndexer('fullname')
        catalog['fullname'] = CatalogTextIndex(fullname)
        email = NodeAttributeIndexer('email')
        catalog['email'] = CatalogTextIndex(email)
        location = NodeAttributeIndexer('location')
        catalog['location'] = CatalogTextIndex(location)
        home_page = NodeAttributeIndexer('home_page')
        catalog['home_page'] = CatalogTextIndex(home_page)
        return catalog


@implementer(ICatalogFactory)
class GroupsSoupCatalogFactory(object):
    """ The local user catalog (LUC) properties index factory. Almost all the
        properties have a field type "FullTextIndex" to allow wildcard queries
        on them. However, the FullTextIndex has a limitation its supported type
        of queries, so for certain operations is needed a FieldIndex for the
        username.

        :index id: FieldIndex - The group id for exact queries
        :index searchable_id: FullTextIndex - The group id used for wildcard
            queries
    """
    def __call__(self, context):
        catalog = Catalog()
        groupindexer = NodeAttributeIndexer('id')
        catalog['id'] = CatalogFieldIndex(groupindexer)
        idsearchableindexer = NodeAttributeIndexer('searchable_id')
        catalog['searchable_id'] = CatalogTextIndex(idsearchableindexer)
        return catalog


@implementer(ICatalogFactory)
class UserNewsSearchSoupCatalog(object):
    def __call__(self, context):
        catalog = Catalog()
        idindexer = NodeAttributeIndexer('id')
        catalog['id'] = CatalogFieldIndex(idindexer)
        hashindex = NodeAttributeIndexer('searches')
        catalog['searches'] = CatalogKeywordIndex(hashindex)

        return catalog


@implementer(ICatalogFactory)
class UsersDeleteLocalRoles(object):
    """ Usuaris esborrats que falta esborrar el local roles
        :index id: TextIndex - id_username = username
    """

    def __call__(self, context):
        catalog = Catalog()
        idindexer = NodeAttributeIndexer('id_username')
        catalog['id_username'] = CatalogTextIndex(idindexer)

        return catalog


@implementer(ICatalogFactory)
class UsersPortrait(object):
    """ Usuaris si tenen la foto del perfil o no DefaultImage
        :index id: TextIndex - id_username = username
        :index portrait: FieldIndex - Boolean, if the username has portrait
    """

    def __call__(self, context):
        catalog = Catalog()
        idindexer = NodeAttributeIndexer('id_username')
        catalog['id_username'] = CatalogTextIndex(idindexer)
        portrait = NodeAttributeIndexer('portrait')
        catalog['portrait'] = CatalogFieldIndex(portrait)

        return catalog