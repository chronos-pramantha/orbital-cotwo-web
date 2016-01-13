from setuptools import setup, find_packages


test_requires = [

]

dev_requires = [
    'numpy',
    'netCDF4',
    'falcon=0.3.0',
    'geojson=1.3.1',
    'sqlalchemy=1.0.11',
    'geoalchemy2=0.2.6',
    'psycopg2=2.6.1'
]

setup(name='oco2web',
      version='0.0.1',
      description=u'NASA OCO-2 mission\'s data API',
      long_description='An API based on NASA\'s CO2 data',
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Service',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development',
      ],
      keywords='co2 emissions geolocate',
      author=u"Lorenzo Moriondo",
      author_email='tunedconsulting@gmail.com',
      url='',
      license='Apache 2.0',
      packages=find_packages(exclude=['examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[

      ],
      extras_require={
          'test': test_requires,
          'dev': test_requires + dev_requires,
      },
      entry_points="""

      """
      )
