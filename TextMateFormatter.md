# TextMate Setup #

Using the bundle editor, change the command for "Run Project Unit Tests" in the python bundle to be something like:

```
cd $TM_PROJECT_DIRECTORY ; nosetests --xml --xml-formatter=nosexml.TextMateFormatter
```

Then trigger the command to see the test results stream into an HTML window.

## Adding Coverage ##

Change the command to:

```
cd $TM_PROJECT_DIRECTORY ; nosetests --xml --xml-formatter=nosexml.TextMateFormatter --with-coverage ${NOSE_EXTRA}
```

I use a project environment variable `NOSE_EXTRA` with the value of a the package I want to cover so I don't have to see a coverage report for all imported modules.