# Description #

Writes a pretty printed XML document.

When I get around to it I'll look at making a Relax-NG schema to validate this against.

For now, typical output would look like this:

```
<?xml version="1.0" encoding="UTF-8"?>
<nosetests>
    <test status="success" id="test.basic_test.Tests.test_1" />
    <test status="success" id="test.basic_test.Tests.test_2">
        <captured>
            Captured output!
        </captured>
    </test>
    <test status="success" id="test.basic_test.Tests.test_3">
        <captured>
            Escape this! &amp;amp;&amp;lt;&amp;amp;&amp;gt;&amp;amp;
        </captured>
    </test>
    <test status="error" id="test.basic_test.Tests.test_4">
        <frame function="run" text="testMethod()" line="260" file="/opt/local/lib/python2.5/unittest.py" />
        <frame function="test_4" text="raise ValueError()" line="18" file="/Users/davisp/project/test/basic_test.py" />
        <cause type="ValueError" />
    </test>
    <test status="failure" id="test.basic_test.Tests.test_5">
        <frame function="run" text="testMethod()" line="260" file="/opt/local/lib/python2.5/unittest.py" />
        <frame function="test_5" text="self.extra_frame( 5 )" line="27" file="/Users/davisp/project/test/basic_test.py" />
        <frame function="extra_frame" text="self.extra_frame( count - 1 )" line="22" file="/Users/davisp/project/test/basic_test.py" />
        <frame function="extra_frame" text="self.extra_frame( count - 1 )" line="22" file="/Users/davisp/project/test/basic_test.py" />
        <frame function="extra_frame" text="self.extra_frame( count - 1 )" line="22" file="/Users/davisp/project/test/basic_test.py" />
        <frame function="extra_frame" text="self.extra_frame( count - 1 )" line="22" file="/Users/davisp/project/test/basic_test.py" />
        <frame function="extra_frame" text="self.extra_frame( count - 1 )" line="22" file="/Users/davisp/project/test/basic_test.py" />
        <frame function="extra_frame" text="self.assertEqual( 1, 'not 1' )" line="24" file="/Users/davisp/project/test/basic_test.py" />
        <frame function="failUnlessEqual" text="(msg or '%r != %r' % (first, second))" line="334" file="/opt/local/lib/python2.5/unittest.py" />
        <cause type="AssertionError">
            1 != 'not 1'
        </cause>
    </test>
    <reports />
    <results ran="5" failures="1" errors="1" />
</nosetests>
```