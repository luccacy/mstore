try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

version = '0.1.0'

setup(name="mstore",
      version=version,
      description='media store',
      long_description="""
media store service
""",
      classifiers=["Development Status :: 1 - Production/Stable",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Programming Language :: Python",
                   "Topic :: Internet :: WWW/HTTP",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      author='zhouyu',
      author_email='zhouyu@rockontrol.com',
      url='http://rockontrol.com',
      zip_safe=False,
      install_requires=['eventlet','webob','iso8601','paste', 'pyparsing','netaddr','requests','pastedeploy', 'routes'],
      packages=find_packages(exclude=['tests']),
      )
