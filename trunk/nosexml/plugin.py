"""A plugin for nosetests to write output in XML
"""

import logging
import os
import sys

from cStringIO import StringIO

from nose.plugins.base import Plugin

log = logging.getLogger( __name__ )


class NullRedirect(object):
    """Redirects all other output into the ether.
    """
    def write(self,mesg):
        pass
    def writeln(self,*args):
        pass



class NoseXML(Plugin):
    """Write Nosetests output in XML
    
        This version of the XML plugin is based on issue140_ on the nosetests
        Google Code site.
        
        .. _issue140: http://code.google.com/p/python-nose/issues/detail?id=140

        Instead of directly creating an XML DOM document and then using classes
        to render the DOM, I opted to go with a more stream oriented output
        using a SAX style writer. Classes that wish to format output to their
        liking should create a class that inherits from XMLFormatter and pass
        the full module and class name as a python path to the --xml-formatter
        command line argument.
        
        Command line arguments:
        
        --xml                           Enable the XML output plugin.
        --xml-formatter=XML_FORMATTER   Provide a class to format the XML
                                        SAX events into the desired format.
                                        Defaults to nosexml.PrettyPrintFormatter.
    """
    name = 'nose-xml'
    enabled = False
    score = 1000 #Make us trump the capture plugin.
    
    def __init__(self):
        self.stringio = StringIO
        self.sys = sys
        self.stdout = []
        self.redirect = NullRedirect()
        self.buffer = None
    
    def options(self,parser,env=os.environ):
        parser.add_option( '--xml', dest='xml_enabled', default=False,
            action="store_true", help="Format output as an XML document.")
        parser.add_option( '--xml-formatter', dest='xml_formatter',
            default='nosexml.PrettyPrintFormatter',
            help="Class that will process the xml document for output." \
                    " The default is to use nosexml.PrettyPrintFormatter" \
                    " which will write the xml document as plain text." )

    def configure(self,options,conf):
        self.enabled = options.xml_enabled
        if not self.enabled or not options.xml_formatter:
            self.enabled = False
            self.formatter = None
        else:
            ( modName, clsName ) = options.xml_formatter.rsplit( '.', 1 )
            __import__(modName)
            self.cls_inst = getattr( sys.modules[modName], clsName )
            self.formatter = self.cls_inst( self.sys.stdout )

    def setOutputStream(self,stream):
        self.formatter.setStream( stream )
        return self.redirect

    def begin(self):
        self._start()
        self.formatter.startDocument()

    def finalize(self,result):
        self.formatter.endDocument()
        while self.stdout:
            self._end()

    def beforeTest(self,test):
        self._start()

    def afterTest(self,test):
        self._end()

    def addSuccess(self,test):
        self.formatter.startElement( 'test', { 'id': test.id(), 'status': 'success' } )
        self._writeCaptured()
        self.formatter.endElement( 'test' )

    def addError(self,test,err):
        self.formatter.startElement( 'test', { 'id': test.id(), 'status': 'error' } )
        self._writeTraceback( err )
        self._writeCaptured()
        self.formatter.endElement( 'test' )
        
    def addFailure(self,test,err):
        self.formatter.startElement( 'test', { 'id': test.id(), 'status': 'failure' } )
        self._writeTraceback( err )
        self._writeCaptured()
        self.formatter.endElement( 'test' )

    def _start(self):
        self.stdout.append( self.sys.stdout )
        self.buffer = self.stringio()
        self.sys.stdout = self.buffer

    def _end(self):
        if self.stdout:
            self.sys.stdout = self.stdout.pop()

    def _writeCaptured(self):
        if self.buffer is not None and self.buffer.getvalue().strip():
            self.formatter.startElement( 'captured' )
            self.formatter.characters( self.buffer.getvalue() )
            self.formatter.endElement( 'captured' )
            self.captured  = None

    def _writeTraceback(self,exc_info):
        import traceback
        for ( fname, line, func, text ) in traceback.extract_tb( exc_info[2] ):
            self.formatter.startElement( 'frame', { 'file': fname, 'line': str(line), 'function': str(func) } )
            self.formatter.characters( text )
            self.formatter.endElement( 'frame' )
        etype = ''.join( [ f.strip() for f in traceback.format_exception_only( exc_info[0], '' ) ] )
        self.formatter.startElement('cause', { 'type': etype } )
        self.formatter.characters( str( exc_info[1] ) )
        self.formatter.endElement( 'cause' )
