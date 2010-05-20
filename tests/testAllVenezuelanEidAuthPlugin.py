# -*- coding: utf-8 -*-
#
# File: testAllVenezuelanEidAuthPlugin.py
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

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

##code-section module-header #fill in your manual code here
from AccessControl import Unauthorized

from AccessControl.SecurityManagement import getSecurityManager

from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName

##/code-section module-header

#
# Test-cases for class(es) 
#

from Testing import ZopeTestCase
from Products.VenezuelanEidAuthPlugin.config import *
from Products.VenezuelanEidAuthPlugin.tests.BaseVenezuelanEidAuthPluginTestCase import BaseVenezuelanEidAuthPluginTestCase

# Import the tested classes

##code-section module-beforeclass #fill in your manual code here
##/code-section module-beforeclass


class testAllVenezuelanEidAuthPlugin(BaseVenezuelanEidAuthPluginTestCase):
    """Test-cases for class(es) ."""

    ##code-section class-header_testAllVenezuelanEidAuthPlugin #fill in your manual code here
    ##/code-section class-header_testAllVenezuelanEidAuthPlugin

    def afterSetUp(self):
        """

        """
        BaseVenezuelanEidAuthPluginTestCase.afterSetup(self)

    # Manually created methods
    def testExtensionsInstall(self):
        #we test if the property called https_address is added into site_properties
        self.failUnless(hasattr(self.portal.portal_properties.site_properties, 'https_address'))

        #we test if the MemberWithEid role exist in PAS
        pas = self.portal.acl_users
        prm = pas.portal_role_manager
        self.failUnless( "MemberWithEid" in prm.listRoleIds())

        #we test if the VenezuelanEidAuthPlugin plugin is added in plonePas
        self.failUnless( hasattr(pas, 'VenezuelanEidAuthPlugin'))

    def testExtractCredentials(self):
        """
         We test if the extractCredentials method do what it has to...
        """
        portal = self.portal
        REQUEST = portal.REQUEST
        SESSION = portal.REQUEST.SESSION
        #we add the plugin
        #portal.acl_users.manage_addProduct['VenezuelanEidAuthPlugin'].manage_addVenezuelanEidAuthPlugin(id='beap')
        beap = portal.acl_users.VenezuelanEidAuthPlugin
        #--------------------> WITHOUT HTTPS <--------------------
        #we check that extractCredentials return None if the REQUEST does not have 'HTTP_SSL_CLIENT_S_DN'
        #weird behaviour of REQUEST that has got every keys ???  We str(REQUEST)...
        self.failIf('HTTP_SSL_CLIENT_S_DN' in str(REQUEST))
        self.failIf(beap.extractCredentials(REQUEST))
        
        #moreover, the SESSION object has not the keys 'eid_nr' and 'eid_from_http'
        self.failIf(SESSION.has_key('eid_nr'))
        self.failIf(SESSION.has_key('eid_from_http'))
        self.failIf(beap.extractCredentials(REQUEST))
        
        #--------------------> WITH HTTPS <--------------------
        #we set 'HTTP_SSL_CLIENT_S_DN' to "/C=VE/CN=User Venezuelan (Authentication)/SN=Venezuelan/GN=User/serialNumber=71715100070"
        REQUEST.set('HTTP_SSL_CLIENT_S_DN', "/C=VE/CN=User Venezuelan (Authentication)/SN=Venezuelan/GN=User/serialNumber=71715100070")
        self.failUnless('HTTP_SSL_CLIENT_S_DN' in str(REQUEST))
        
        #extractCredentials will return the creds
        creds = ({'eid_nr': '71715100070',
                  'eid_from_http': 1,
                  'eid_http_ssl_client_s_dn': "/C=VE/CN=User Venezuelan (Authentication)/SN=Venezuelan/GN=User/serialNumber=71715100070"
                 })
        #first time we extractCredentials, the credentials are set in SESSION
        self.assertEquals(beap.extractCredentials(REQUEST), creds)
        self.failUnless(SESSION.has_key('eid_nr'))
        self.failUnless(SESSION.has_key('eid_from_http'))
        
        #when extractCredentials has returned the credentials once, it will always return them
        self.assertEquals(beap.extractCredentials(REQUEST), creds)

        #we check if we change the 'HTTP_SSL_CLIENT_S_DN' if the user is no more recongnized and the process of authentication start again
        old_creds = beap.extractCredentials(REQUEST)
        REQUEST.set('HTTP_SSL_CLIENT_S_DN', "/C=VE/CN=User2 Venezuelan2 (Authentication)/SN=Venezuelan2/GN=User2/serialNumber=71715100070")
        self.assertNotEquals(beap.extractCredentials(REQUEST), old_creds)
        
        #check if Apache remove the 'HTTP_SSL_CLIENT_S_DN' from the REQUEST
        REQUEST.set('HTTP_SSL_CLIENT_S_DN', None)
        self.failIf(beap.extractCredentials(REQUEST))
        #when Apache has just removed 'HTTP_SSL_CLIENT_S_DN' from the REQUEST, we must be sure that extractCredentials has cleaned up SESSION : keys 'eid_from_http', 'eid_nr', 'eid_http_ssl_client_s_dn' and 'eid_username' must have been removed
        self.failIf(SESSION.has_key('eid_nr'))
        self.failIf(SESSION.has_key('eid_from_http'))
        self.failIf(SESSION.has_key('eid_http_ssl_client_s_dn'))
        self.failIf(SESSION.has_key('eid_username'))
        #we call extractCredentials again to test the try with del request.SESSION
        self.failIf(beap.extractCredentials(REQUEST))


    def testGetClientData(self):
        """
         We test the getClientData() method that returns the credentials from 'HTTP_SSL_CLIENT_S_DN'
        """
        portal = self.portal
        #we add the plugin
        #portal.acl_users.manage_addProduct['VenezuelanEidAuthPlugin'].manage_addVenezuelanEidAuthPlugin(id='beap')
        beap = portal.acl_users.VenezuelanEidAuthPlugin
        
        from_http = None
        self.failIf(beap.getClientData(from_http))
        
        #we set the from_http with some wrong values and we test
        #not valid
        from_http = "1"
        self.failIf(beap.getClientData(from_http))
        #not valid
        from_http = "12345678910"
        self.failIf(beap.getClientData(from_http))
        #not a valid serialNumber
        from_http = "/C=VE/CN=User Venezuelan (Authentication)/SN=Venezuelan/GN=User/serialNumber=1234567891"
        self.failIf(beap.getClientData(from_http))
        
        #we check that a valid 'HTTP_SSL_CLIENT_S_DN' can be evaluated to return the serialNumber
        from_http = "/C=VE/CN=User Venezuelan (Authentication)/SN=Venezuelan/GN=User/serialNumber=71715100070"
        self.assertEquals(beap.getClientData(from_http), "71715100070")


    def testAuthenticateCredentials(self):
        """
         We test if the authenticateCredentials method do what it has to...
        """
        portal = self.portal
        REQUEST = portal.REQUEST
        SESSION = portal.REQUEST.SESSION
        #we add the plugin
        #portal.acl_users.manage_addProduct['VenezuelanEidAuthPlugin'].manage_addVenezuelanEidAuthPlugin(id='beap')
        beap = portal.acl_users.VenezuelanEidAuthPlugin
        
        #--------------------> CREDENTIALS WITHOUT 'eid_from_http' KEY <--------------------
        #if the credentials returned by extractCredentials is None, authenticateCredentials must return None too...
        credentials = {}
        self.failIf(beap.authenticateCredentials(credentials))
        
        #if the credentials returned by extractCredentials do not have the key 'eid_from_http', authenticateCredentials return None
        credentials = ({'eid_nr': '71715100070'})
        self.failIf(beap.authenticateCredentials(credentials))
        
        #--------------------> CREDENTIALS WITH 'eid_from_http' KEY <--------------------
        #--------------------> USER DOES NOT EXIST <--------------------
        #credentials is well formatted
        #but has not the 'eid_username' key
        credentials = ({'eid_nr': '71715100070',
                  'eid_from_http': 1,
                  'eid_http_ssl_client_s_dn': "/C=VE/CN=User Venezuelan (Authentication)/SN=Venezuelan/GN=User/serialNumber=71715100070"
                 })
        #authenticateCredentials will look up the user
        #if the user does not exist, authenticateCredentials return None
        self.failIf(beap.authenticateCredentials(credentials))
        #and 'eid_username' is not set in SESSION
        self.failIf(SESSION.get('eid_username'))

        #--------------------> USER EXISTS <--------------------
        #now, we add the user in acl_users and we try to authenticateCredentials...
        #in order to search the user upon his national register number, and so for the 'getUserNameFromNR' to work, we need to add a property to portal_memberdata called 'nationalregister' and to fill it.  This can be done in Plone using the CPDescriptive product...
        portal.portal_memberdata.manage_addProperty('nationalregister', '', 'string')
        #addMember need id, password, and if we enter some properties, we have to specify the username and email too...
        pr_tool = getToolByName(portal, 'portal_registration')
        pr_tool.addMember('user', '12345', properties={'username':'User',
                                                       'email':'user@user.be',
                                                       'nationalregister':'71715100070'})
        #the user exist, authenticateCredentials must return this user
        self.assertEquals(beap.authenticateCredentials(credentials), ('user', 'user'))
        #if the user has been found, authenticateCredentials set 'eid_username' is SESSION
        self.assertEquals(SESSION.get('eid_username'), "user")
        
    def testGetUserNameFromNR(self):
        """
         We test that getUserNameFromNR work correctly
        """
        portal = self.portal
        REQUEST = portal.REQUEST
        SESSION = portal.REQUEST.SESSION
        #we add the plugin
        #portal.acl_users.manage_addProduct['VenezuelanEidAuthPlugin'].manage_addVenezuelanEidAuthPlugin(id='beap')
        beap = portal.acl_users.VenezuelanEidAuthPlugin

        nr = "71715100070"
                
        #--------------------> USER DOES NOT EXIST <--------------------
        #if the user does not exists, the method obviously return None but it work even if the 'nationalregister' property does not exist in portal_memberdata
        self.failIf(beap.getUserNameFromNR(nr))
        
        #--------------------> USER EXISTS <--------------------
        #we add the 'nationalregister' porperty in portal_memberdata
        portal.portal_memberdata.manage_addProperty('nationalregister', '', 'string')
        pr_tool = getToolByName(portal, 'portal_registration')
        #we add a user with a valid 'nationalregister'
        #addMember need id, password, and if we enter some properties, we have to specify the username and email too...
        pr_tool.addMember('user', '12345', properties={'username':'User',
                                                       'email':'user@user.be',
                                                       'nationalregister':'71715100070'})
        #now it should work...
        self.assertEquals(beap.getUserNameFromNR(nr), "user")


    def testExtractAndAuthenticateCredentials(self):
        """
         As extractCredentials and authenticateCredentials are linked, we have to test them together too...
         What we have to test here is what is modified in extractCredentials and used in authenticateCredentials : the 'eid_username' key from SESSION
        """
        portal = self.portal
        REQUEST = portal.REQUEST
        SESSION = portal.REQUEST.SESSION
        #we add the plugin
        #portal.acl_users.manage_addProduct['VenezuelanEidAuthPlugin'].manage_addVenezuelanEidAuthPlugin(id='beap')
        beap = portal.acl_users.VenezuelanEidAuthPlugin
        #we add the 'nationalregister' porperty in portal_memberdata
        portal.portal_memberdata.manage_addProperty('nationalregister', '', 'string')
        pr_tool = getToolByName(portal, 'portal_registration')
        #we add a user with a valid 'nationalregister'
        #addMember need id, password, and if we enter some properties, we have to specify the username and email too...
        pr_tool.addMember('user', '12345', properties={'username':'User',
                                                       'email':'user@user.be',
                                                       'nationalregister':'71715100070'})

        REQUEST.set('HTTP_SSL_CLIENT_S_DN', "/C=VE/CN=User Venezuelan (Authentication)/SN=Venezuelan/GN=User/serialNumber=71715100070")
        #we extract credentials ...
        creds = beap.extractCredentials(REQUEST)
        #... and the user must have been authenticated
        self.assertEquals(beap.authenticateCredentials(creds), ('user', 'user'))
        #the 'eid_username' key must be set in the SESSION
        self.failUnless(SESSION.has_key('eid_username'))
        
        #if we change the 'HTTP_SSL_CLIENT_S_DN' (as Apache could do), the 'eid_username' key must have disappeared after extractCredentials but must be set after authenticateCredentials if the serialNumber is found in the users 'nr'
        REQUEST.set('HTTP_SSL_CLIENT_S_DN', "/C=VE/CN=User2 Venezuelan2 (Authentication)/SN=Venezuelan/GN=User/serialNumber=71715100070")
        
        creds = beap.extractCredentials(REQUEST)
        self.failIf(SESSION.has_key('eid_username'))
        beap.authenticateCredentials(creds)
        self.failUnless(SESSION.has_key('eid_username'))
        
        #if we change the 'HTTP_SSL_CLIENT_S_DN' AND the serialNumber is not found in the users 'nr', the 'eid_username' key can not be set in SESSION after extractCredentials and after authenticateCredentials
        REQUEST.set('HTTP_SSL_CLIENT_S_DN', "/C=VE/CN=User2 Venezuelan2 (Authentication)/SN=Venezuelan/GN=User/serialNumber=71715100169")
        creds = beap.extractCredentials(REQUEST)
        self.failIf(SESSION.has_key('eid_username'))
        beap.authenticateCredentials(creds)
        self.failIf(SESSION.has_key('eid_username'))
        

    def testLoggedInScriptExecutedWithNotRedirectableURL(self):
        """
         We want the logged_in.cpy script to be executed each time we connect (and only once)
        """
        portal = self.portal
        REQUEST = portal.REQUEST
        SESSION = portal.REQUEST.SESSION
        #we add the plugin
        #portal.acl_users.manage_addProduct['VenezuelanEidAuthPlugin'].manage_addVenezuelanEidAuthPlugin(id='beap')
        beap = portal.acl_users.VenezuelanEidAuthPlugin
        #we add the 'nationalregister' porperty in portal_memberdata
        portal.portal_memberdata.manage_addProperty('nationalregister', '', 'string')
        pr_tool = getToolByName(portal, 'portal_registration')
        #we add a user with a valid 'nationalregister'
        #addMember need id, password, and if we enter some properties, we have to specify the username and email too...
        pr_tool.addMember('user', '12345', properties={'username':'User',
                                                       'email':'user@user.be',
                                                       'nationalregister':'71715100070'})

        REQUEST.set('HTTP_SSL_CLIENT_S_DN', "/C=VE/CN=User Venezuelan (Authentication)/SN=Venezuelan/GN=User/serialNumber=71715100070")
        #'logged_out' will not be redirected by login_next
        REQUEST.set('URL', "logged_out")
        
        creds = beap.extractCredentials(REQUEST)
        #we verify that the logged_in.cpy script is executed if we are not using a not_redirectable_url
        self.failIf(SESSION.has_key('eid_logged_in_executed'))
        beap.authenticateCredentials(creds)
        self.failIf(SESSION.has_key('eid_logged_in_executed'))
        
        #we put a redirectable URL in REQUEST/'URL'
        REQUEST.set('URL', "redirectable_url")
        beap.authenticateCredentials(creds)
        self.failUnless(SESSION.has_key('eid_logged_in_executed'))
        
        
    def testLoggedInScriptExecutedWithRedirectableURL(self):
        """
         We want the logged_in.cpy script to be executed each time we connect (and only once)
        """
        portal = self.portal
        REQUEST = portal.REQUEST
        SESSION = portal.REQUEST.SESSION
        #we add the plugin
        #portal.acl_users.manage_addProduct['VenezuelanEidAuthPlugin'].manage_addVenezuelanEidAuthPlugin(id='beap')
        beap = portal.acl_users.VenezuelanEidAuthPlugin
        #we add the 'nationalregister' porperty in portal_memberdata
        portal.portal_memberdata.manage_addProperty('nationalregister', '', 'string')
        pr_tool = getToolByName(portal, 'portal_registration')
        #we add a user with a valid 'nationalregister'
        #addMember need id, password, and if we enter some properties, we have to specify the username and email too...
        pr_tool.addMember('user', '12345', properties={'username':'User',
                                                       'email':'user@user.be',
                                                       'nationalregister':'71715100070'})

        REQUEST.set('HTTP_SSL_CLIENT_S_DN', "/C=VE/CN=User Venezuelan (Authentication)/SN=Venezuelan/GN=User/serialNumber=71715100070")
        
        creds = beap.extractCredentials(REQUEST)
        #we verify that the logged_in.cpy script is executed if we are not using a not_redirectable_url
        self.failIf(SESSION.has_key('eid_logged_in_executed'))
        beap.authenticateCredentials(creds)
        self.failUnless(SESSION.has_key('eid_logged_in_executed'))
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testAllVenezuelanEidAuthPlugin))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


