import sys
import unittest

from optparse import OptionParser

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from nose.plugins.capture import Capture
from nose.plugins import PluginTester

from nosexml import NoseXML, NullRedirect, PrettyPrintFormatter

class TestNullRedirect(unittest.TestCase):
    def test_basic(self):
        nr = NullRedirect()
        nr.write( 'missing' )
        nr.writeln( 'ignoring' )

class TestPreConfiguredNoseXML(unittest.TestCase):

    def setUp(self):
        self.pi = NoseXML()

    def test_constructor(self):
        self.assertEqual( self.pi.stringio, StringIO )
        self.assertEqual( self.pi.sys, sys )
        self.assertEqual( self.pi.stdout, [] )
        self.assertEqual( self.pi.redirect.__class__, NullRedirect )
        self.assertEqual( self.pi.buffer, None )
        
    def test_option(self):
        parser = OptionParser()
        self.pi.options( parser, env={} )
        self.assertEqual( parser.has_option( '--xml' ), True )
        self.assertEqual( parser.has_option( '--xml-formatter' ), True )
        opt = parser.get_option( '--xml' )
        self.assertEqual( opt.action, 'store_true' )
        self.assertEqual( opt.default, False )
        opt = parser.get_option( '--xml-formatter' )
        self.assertEqual( opt.action, 'store' )
        self.assertEqual( opt.default, 'nosexml.PrettyPrintFormatter' )

    def test_configure(self):
        class Foo(object):
            pass
        opts = Foo()
        opts.xml_enabled = True
        opts.xml_formatter = 'nosexml.PrettyPrintFormatter'
        self.pi.configure( opts, {} )
        self.assertEqual( self.pi.enabled, True )
        self.assertEqual( self.pi.formatter.__class__, PrettyPrintFormatter )
        opts.xml_enabled = False
        self.pi.configure( opts, {} )
        self.assertEqual( self.pi.enabled, False )
        self.assertEqual( self.pi.formatter, None )
        opts.xml_enabled = True
        opts.xml_formatter = None
        self.pi.configure( opts, {} )
        self.assertEqual( self.pi.enabled, False )
        self.assertEqual( self.pi.formatter, None )

class TestPostConfiguredNoseXML(unittest.TestCase):
    def setUp(self):
        self.pi = NoseXML()
        class Foo(object):
            pass
        opts = Foo()
        opts.xml_enabled = True
        opts.xml_formatter = 'nosexml.PrettyPrintFormatter'
        self.pi.configure( opts, {} )

    def test_set_output(self):
        strm = 1
        ret = self.pi.setOutputStream( strm )
        self.assertEqual( self.pi.formatter.stream, 1 )
        self.assertEqual( ret.__class__, NullRedirect )

class UnitTest(object):
    def id(self):
        return 'test.class_name'

class TestFormatter(PrettyPrintFormatter):
    pass

class TestStreamSetNoseXML(unittest.TestCase):
    def setUp(self):
        self.pi = NoseXML()
        class Foo(object):
            pass
        opts = Foo()
        opts.xml_enabled = True
        opts.xml_formatter = 'test.plugin_test.TestFormatter'
        self.pi.configure( opts, {} )
        self.buffer = StringIO()
        self.pi.setOutputStream( self.buffer )

    def test_other_formatter_class(self):
        self.assertEqual( self.pi.formatter.__class__, TestFormatter )

    def test_begin_finalize(self):
        curr_stdout = sys.stdout
        self.pi.begin()
        self.assertNotEqual( sys.stdout, curr_stdout )
        self.assertEqual( self.pi.stdout, [ curr_stdout ] )
        self.assertEqual( self.pi.buffer, sys.stdout )
        self.pi.finalize( '' )
        self.assertEqual( self.pi.stdout, [] )
        self.assertEqual( sys.stdout, curr_stdout )
        self.assertEqual( self.buffer.getvalue(), '<?xml version="1.0" encoding="UTF-8"?>\n' \
                                                    '<nosetests>\n</nosetests>\n' )

    def test_finalize_wo_begin(self):
        self.pi.finalize( '' )

    def test_before_after_test(self):
        self.pi.beforeTest(None)
        print "hi mom"
        self.pi.afterTest(None)
        self.assertEqual( self.pi.buffer.getvalue(), "hi mom\n" )

    def test_add_success(self):
        self.pi.addSuccess( UnitTest() )
        self.assertEqual( self.buffer.getvalue(),
            '    <test status="success" id="test.class_name" />\n' )

    #Below here I don't test other than the implicit "doesn't throw"
    #In the future I'll have to come back through with an xml parser
    #or fill out the TestFormatter with event expectation stuff.
    def test_success_with_captured(self):
        self.pi.begin()
        t = UnitTest()
        self.pi.beforeTest( t )
        print "Hi!"
        self.pi.afterTest( t )
        self.pi.addSuccess( t )
        self.pi.finalize( '' )

    def test_add_error(self):
        try:
            raise ValueError()
        except:
            self.pi.addError( UnitTest(), sys.exc_info() )

    def test_add_failure(self):
        try:
            raise AssertionError()
        except:
            self.pi.addFailure( UnitTest(), sys.exc_info() )