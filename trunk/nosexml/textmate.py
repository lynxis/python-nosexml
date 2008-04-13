"""
Copyright (c) 2008 Paul Davis <paul.joseph.davis@gmail.com>

This file is part of nosexml, which is released under the MIT license.
"""

import urllib
from formatter import XMLFormatter

html = {
'header': """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html>
    <head>
        <title>Nosetests Error Report</title>
        <style type="text/css">
            body
            {
                font-family: Lucida Grande ;
            }
        
            a
            {
                color: blue ;
                text-decoration: none ;
            }
        
            ul
            {
                padding: 0px ;
                margin: 0px ;
                list-style-type: none ;
            }
            
            ul li
            {
                padding: 5px ;
                margin: 0px ;
                margin-bottom: 5px ;
                border: 1px solid #CCCCCC ;
            }
            
            h2
            {
                display: inline ;
                margin: 0px ;
                padding: 0px ;
                font-size : 14px ;
            }
            
            ul li.success h2
            {
                color: green ;
            }
            
            ul li.error h2
            {
                color: orange ;
            }
            
            ul li.failure h2
            {
                color: red ;
            }
            
            ul.traceback li
            {
                border: none ;
                padding: 0px ;
                margin: 0px ;
            }
            
            ul.traceback li pre
            {
                padding: 0px ;
                margin: 0px ;
            }
            
            div.content
            {
                margin: 10px ;
                margin-left: 25px ;
                font-size: 12px ;
            }
        </style>
        <script type="text/javascript">
            function scroll_to_bottom()
            {
                var height = document.documentElement.clientHeight ;
                window.scrollTo( 0, height ) ;
            }
            
            function toggle( id, action )
            {
                var d = document.getElementById( id ) ;
                var s = document.getElementById( id + "_s" ) ;
                var h = document.getElementById( id + "_h" ) ;
                
                if( action == 'hide' )
                {
                    d.style.display = "none" ;
                    s.style.display = "inline" ;
                    h.style.display = "none" ;
                }
                else if( action == "show" )
                {
                    d.style.display = "block" ;
                    s.style.display = "none" ;
                    h.style.display = "inline" ;
                }
            }
        </script>
    </head>
    <body>
        <ul>
""",

'start_test': """
            <li class="%(status)s">
                <a href="javascript:toggle( '%(id)s', 'show' )" id="%(id)s_s">&#x25B6;</a>
                <a href="javascript:toggle( '%(id)s', 'hide' )" id="%(id)s_h" style="display: none;">&#x25BC;</a>
                <h2>%(id)s</h2>
                <div id="%(id)s" class="content" style="display: none;">
""",

'start_traceback': """
                    <ul class="traceback">
""",

'start_frame': """
                        <li>
                            <tt><a href="txmt://open?url=%(url)s&line=%(line)s">%(file)s(%(line)s): %(function)s</a></tt>
                            <pre>    %(text)s</pre>
                        </li>
""",

'start_cause': """<li><pre>%(type)s: """,

'end_cause': """</pre></li>""",

'end_frame': """
""",

'end_traceback': """
                    </ul>
""",

'start_captured': """<pre>""",

'end_captured': """</pre>""",

'end_test': """
                </div>
                <script type="text/javascript">
                    scroll_to_bottom() ;
                </script>
            </li>
""",

'start_reports': """
            <li>
                <a href="javascript:toggle( 'reports', 'show' )" id="reports_s">&#x25B6;</a>
                <a href="javascript:toggle( 'reports', 'hide' )" id="reports_h" style="display: none;">&#x25BC;</a>
                <h2>Reports</h2>
                <div id="reports" class="content" style="display: none;"><pre>""",

'end_reports': '</pre></div></li>',

'start_results': """
            <li>
                <em>Ran</em> %(ran)s
                <em>Errors</em> %(errors)s
                <em>Failures</em> %(failures)s
            </li>
""",

'end_results': '',

'footer': """
        </ul>
        <script type="text/javascript">
            scroll_to_bottom() ;
        </script>
    </body>
</html>
"""

}

class TextMateFormatter(XMLFormatter):
    def __init__(self,stream):
        self.stream = stream
        self.state = []

    def setStream(self,stream):
        self.stream = stream

    def startDocument(self):
        self.stream.write( html['header'] )
        self.stream.flush()
        
    def endDocument(self):
        self.stream.write( html['footer'] )
        self.stream.flush()

    def startElement(self,name,attrs):
        if name == 'test':
            self.state.append( 'test' )
            self.stream.write( html['start_test'] % attrs )
        elif name == 'frame' and self.state[-1] != 'traceback':
            self.state.append( 'traceback' )
            self.state.append( 'frame' )
            self.stream.write( html['start_traceback'] )
            attrs['url'] = 'file://%s' % urllib.quote( attrs['file'] )
            self.stream.write( html['start_frame'] % attrs )
        elif name == 'frame':
            self.state.append( 'frame' )
            attrs['url'] = 'file://%s' % urllib.quote( attrs['file'] )
            self.stream.write( html['start_frame'] % attrs )
        elif name == 'captured':
            self.state.append( 'captured' )
            self.stream.write( html['start_captured'] % attrs )
        elif name == 'cause':
            self.state.append( 'cause' )
            self.stream.write( html['start_cause'] % attrs )
        elif name == 'reports':
            self.state.append( 'reports' )
            self.stream.write( html['start_reports'] % attrs )
        elif name == 'results':
            self.state.append( 'results' )
            self.stream.write( html['start_results'] % attrs )
        else:
            raise ValueError( "Unexpected element name: %s" % name )
        self.stream.flush()

    def endElement(self,name):
        curr = self.state.pop()
        while curr != name:
            self.stream.write( html['end_%s' % curr] )
            curr = self.state.pop()
        self.stream.write( html[ 'end_%s' % name ] )
        self.stream.flush()

    def characters(self,data):
        self.stream.write( data.strip() )
        self.stream.flush()
