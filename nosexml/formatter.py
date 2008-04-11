class XMLFormatter(object):
    """Base XMLFormatter class

        For those wanting to design their own XML output format, this is
        the class that should be inherited and passed to nosetests in the
        --xml-formatter command line argument.
        
        All in all its fairly simple. You should mostly think of it as a
        reverse SAX parser. 
    """
    def __init__(self,stream):
        self.stream = stream
    def setStream(self,stream):
        raise NotImplementedError()
    def startDocument(self):
        raise NotImplementedError()
    def endDocument(self):
        raise NotImplementedError()
    def startElement(self,name,attrs={}):
        raise NotImplementedError()
    def endElement(self,name):
        raise NotImplementedError()
    def characters(self,data):
        raise NotImplementedError()
