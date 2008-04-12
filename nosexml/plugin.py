"""A plugin for nosetests to write output in XML

Copyright (c) 2008 Paul Davis <paul.joseph.davis@gmail.com>

This file is part of nosexml, which is released under the MIT license.
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
    def __init__(self):
        self.buf = StringIO()
    def write(self,mesg):
        self.buf.write( mesg )
    def writeln(self,*args):
        if len( args ) > 0:
            self.buf.write( '%s\n' % args )
        else:
            self.buf.write( '\n' )

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
    score = 499 #Just trump the capture plugin.
    
    def __init__(self):
        self.stringio = StringIO
        self.sys = sys
        self.stdout = []
        self.redirect = NullRedirect()
        self.buffer = None
        self.ran = 0
        self.errors = 0
        self.failures = 0
    
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
        self.old_stream = stream
        return self.redirect

    def prepareTestResult(self,result):
        #Monkey patch the TextTestResult to not print
        #it's summary.
        result.dots = False
        def _mpPrintSummary(start,stop):
            pass
        result.printSummary = _mpPrintSummary

    def begin(self):
        self._start()
        self.formatter.startDocument()

    def finalize(self,result):
        self.formatter.startElement( 'reports', attrs={} )
        self.formatter.characters( self._escape( self.redirect.buf.getvalue() ) )
        self.formatter.endElement( 'reports' )
        self.formatter.startElement( 'results', attrs={ 'ran': self.ran, 'errors': self.errors, 'failures': self.failures } )
        self.formatter.endElement( 'results' )
        self.formatter.endDocument()
        while self.stdout:
            self._end()

    def beforeTest(self,test):
        self.ran += 1
        self._start()

    def afterTest(self,test):
        self._end()

    def addSuccess(self,test):
        self.formatter.startElement( 'test', { 'id': test.id(), 'status': 'success' } )
        self._writeCaptured()
        self.formatter.endElement( 'test' )

    def handleError(self,test,err):
        self.errors += 1
        self.formatter.startElement( 'test', { 'id': test.id(), 'status': 'error' } )
        self._writeTraceback( err )
        self._writeCaptured()
        self.formatter.endElement( 'test' )
        return True
        
    def handleFailure(self,test,err):
        self.failures += 1
        self.formatter.startElement( 'test', { 'id': test.id(), 'status': 'failure' } )
        self._writeTraceback( err )
        self._writeCaptured()
        self.formatter.endElement( 'test' )
        return True

    def _start(self):
        self.stdout.append( self.sys.stdout )
        self.buffer = self.stringio()
        self.sys.stdout = self.buffer

    def _end(self):
        if self.stdout:
            self.sys.stdout = self.stdout.pop()

    def _writeCaptured(self):
        if self.buffer is not None and self.buffer.getvalue().strip():
            self.formatter.startElement( 'captured', attrs={} )
            captured = self._escape( self.buffer.getvalue() )
            self.formatter.characters( captured )
            self.formatter.endElement( 'captured' )
            self.captured  = None

    def _writeTraceback(self,exc_info):
        import traceback
        for ( fname, line, func, text ) in traceback.extract_tb( exc_info[2] ):
            fname = self._escape( fname )
            line = self._escape( line )
            func = self._escape( func )
            text = self._escape( text )
            self.formatter.startElement( 'frame', { 'file': fname, 'line': line, 'function': func, 'text': text } )
            self.formatter.endElement( 'frame' )
        etype = ''.join( [ f.strip() for f in traceback.format_exception_only( exc_info[0], '' ) ] )
        etype = self._escape( etype )
        cause = self._escape( exc_info[1] )
        self.formatter.startElement('cause', { 'type': etype } )
        self.formatter.characters( cause )
        self.formatter.endElement( 'cause' )
        
    def _escape(self,data):
        ret = str( data )
        return ret.replace( '&', '&amp;' ).replace( '<', '&lt;' ).replace( '>', '&gt;' )



