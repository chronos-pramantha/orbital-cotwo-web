from setuptools import setup, find_packages


test_requires = [

]

dev_requires = [
    'numpy=1.10.2',
    'netCDF4=1.2.2',
    'falcon=0.3.0',
    'geojson=1.3.1',
    'sqlalchemy=1.0.11',
    'geoalchemy2=0.2.6',
    'psycopg2=2.6.1',
    'pygeoif=0.6'
]

setup(name='oco2web',
      version='0.0.1beta',
      description=u'NASA OCO-2 mission\'s data API',
      long_description='An API based on NASA\'s CO2 data',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Service',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Topic :: Scientific/Engineering :: GIS'
      ],
      keywords='co2 emissions geolocate satallites data',
      author=u"Lorenzo Moriondo",
      author_email='tunedconsulting@gmail.com',
      url='http://earth.projectchronos.org',
      license='Apache 2.0',
      packages=find_packages(exclude=['examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=dev_requires,
      extras_require={
          'test': test_requires,
          'dev': test_requires + dev_requires,
      },
      entry_points="""

      """
      )
