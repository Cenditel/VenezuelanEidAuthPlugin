# -*- coding: utf-8 -*-
#
# File: __init__.py
#
# Copyright (c) 2006 by CommunesPlone
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Gauthier BASTIEN <gbastien@commune.sambreville.be>"""
__docformat__ = 'plaintext'

from AccessControl.Permissions import add_user_folders
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
from VenezuelanEidAuthPlugin import VenezuelanEidAuthPlugin, manage_addVenezuelanEidAuthPlugin, manage_addVenezuelanEidAuthPluginForm
from Products.CMFCore.DirectoryView import registerDirectory

registerDirectory('skins', globals())
registerDirectory('skins/VenezuelanEidAuthPlugin', globals())

def initialize(context):
    """ Initialize the VenezuelanEidAuthPlugin """
    
    registerMultiPlugin(VenezuelanEidAuthPlugin.meta_type)
    
    context.registerClass( VenezuelanEidAuthPlugin
                            , permission=add_user_folders
                            , constructors=( manage_addVenezuelanEidAuthPluginForm
                                        , manage_addVenezuelanEidAuthPlugin
                                        )
                             , icon='www/chip_eid.gif'
                            , visibility=None
                            )