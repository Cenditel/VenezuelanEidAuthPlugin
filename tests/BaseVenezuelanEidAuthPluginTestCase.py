# -*- coding: utf-8 -*-
#
# File: BaseVenezuelanEidAuthPluginTestCase.py
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

#
# Base TestCase for VenezuelanEidAuthPlugin
#

import os, sys, code
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

##code-section module-header #fill in your manual code here
from Products.CMFCore.utils import getToolByName
from sets import Set
##/code-section module-header

from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
from Products.VenezuelanEidAuthPlugin.config import HAS_PLONEPAS
from Products.Archetypes.tests.utils import DummySessionDataManager

# Add common dependencies
if not HAS_PLONEPAS:
    raise importError
    
DEPENDENCIES = []
#DEPENDENCIES.append('CPDescriptive')

# Install all (product-) dependencies, install them too
for dependency in DEPENDENCIES:
    ZopeTestCase.installProduct(dependency)

ZopeTestCase.installProduct('VenezuelanEidAuthPlugin')

PRODUCTS = list()
PRODUCTS += DEPENDENCIES
PRODUCTS.append('VenezuelanEidAuthPlugin')

testcase = PloneTestCase.PloneTestCase

##code-section module-before-plone-site-setup #fill in your manual code here
##/code-section module-before-plone-site-setup

PloneTestCase.setupPloneSite(products=PRODUCTS)

class BaseVenezuelanEidAuthPluginTestCase(testcase):
    """Base TestCase for VenezuelanEidAuthPlugin."""

    ##code-section class-header_BaseVenezuelanEidAuthPluginTestCase #fill in your manual code here
    def afterSetup(self):
        """
        Manage users and permissions
        """
        uf = self.portal.acl_users
        uf.userFolderAddUser('owner', 'owner', ['Member', ], [])
        uf.userFolderAddUser('member', 'member', ['Member', ], [])
        uf.userFolderAddUser('admin', 'admin', ['Manager', 'Member', ], [])
        uf.userFolderAddUser('anon', 'anon', ['Anonymous', ], [])
        self.wft = self.portal.portal_workflow
        request = self.app.REQUEST
        self.app._setObject('session_data_manager', DummySessionDataManager())
        sdm = self.app.session_data_manager
        request.set('SESSION', sdm.getSessionData())
        

    def checkActionList(self, object, actions):
        """ Compare un set d'action de sorte que ['corriger', 'attendre'] soit egal a ['attendre', 'corriger'] """
        obj_actions = self.getActionList(object)
        self.assertEquals(Set(obj_actions), Set(actions))

    def getActionList(self, object):
        return [action_dict['name'] for action_dict in self.wft.getTransitionsFor(object)]
    ##/code-section class-header_BaseVenezuelanEidAuthPluginTestCase

    # Commented out for now, it gets blasted at the moment anyway.
    # Place it in the protected section if you need it.
    #def afterSetup(self):
    #    """
    #    """
    #    pass

    def interact(self, locals=None):
        """Provides an interactive shell aka console inside your testcase.

        It looks exact like in a doctestcase and you can copy and paste
        code from the shell into your doctest. The locals in the testcase are
        available, becasue you are in the testcase.

        In your testcase or doctest you can invoke the shell at any point by
        calling::

            >>> self.interact( locals() )

        locals -- passed to InteractiveInterpreter.__init__()
        """
        savestdout = sys.stdout
        sys.stdout = sys.stderr
        sys.stderr.write('='*70)
        console = code.InteractiveConsole(locals)
        console.interact("""
ZopeTestCase Interactive Console
(c) BlueDynamics Alliance, Austria - 2005

Note: You have the same locals available as in your test-case.
""")
        sys.stdout.write('\nend of ZopeTestCase Interactive Console session\n')
        sys.stdout.write('='*70+'\n')
        sys.stdout = savestdout


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BaseVenezuelanEidAuthPluginTestCase))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()