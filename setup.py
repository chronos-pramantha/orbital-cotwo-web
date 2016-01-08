# Copyright 2016 Pramantha, Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages


test_requires = [

]

dev_requires = [
    'numoy',
    'netCDF4',
    'falcon',
    'geojson'
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
      author_email='',
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
