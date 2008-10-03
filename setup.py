"""
setup.py for nosexml
"""
try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass

from setuptools import setup

setup(
    name='nosexml',
    version='0.1',
    author='Paul Davis',
    author_email = 'davisp@neb.com',
    description = 'Format nosetests output in xml',
    url = "http://code.google.com/p/python-nosexml/",
    download_url = "http://python-nosexml.googlecode.com/svn/trunk/#egg=nosexml-dev",
    license = 'MIT',
    packages = ['nosexml'],
    entry_points = {
        'nose.plugins.0.10': [
            'nose-xml = nosexml:NoseXML'
            ]
        }
    )
