VenezuelanEidAuthPlugin Overview

 VenezuelanEidAuthPlugin is a PAS Plugin that gives the user the possibility to identify himself using is Venezuelan electronic identity card. 

 This plugin can be used together with other PAS Plugins.

 This product should be installed together with CPDescriptive that extends users descriptive. 

 It will automatically add a "nationalregister" property to the portal_memberdata tool. If you do not want to use CPDescriptive, make sure a "nationalregister" property exists in portal_memberdata or it will not be possible to connect to the Plone Site using this plugin.

 A correctly configured web server (Apache, IIS, ...) has to be configured to accept HTTPS and SSL certificates. See the documentation on www.communesplone.org.

 After installing the product, define the https address the connection will have to redirect to in ZMI -> portal_properties, fill the https_address property.
