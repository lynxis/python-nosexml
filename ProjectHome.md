The main plugin generates a series of SAX-like events that can be custom formatted into an XML document.

The default formatter provides a simple XML document listing each test and its status, any associated traceback information and captured output.

# Installation #
```
$ easy_install nosexml
```

I may or may not have gotten everything with cheese shop setup correctly. Feel free to add an issue if something is wonky.

# Added Command Line Options #

| `--xml` | Enable the plugin. Defaults to disabled |
|:--------|:----------------------------------------|
| `--xml-formatter=XML_FORMATTER` | Provide the plugin with the class name that should format the output. Defaults to nosexml.PrettyPrintFormatter |
| `--xml-no-stderr` | Disable capturing of stderr. Useful for catching exceptions that get captured but abort the application. |