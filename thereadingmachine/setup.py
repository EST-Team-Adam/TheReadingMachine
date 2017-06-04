from setuptools import setup
from setuptools import find_packages

long_description = 'Helper function for the Reading Machine'

setup(name='thereadingmachine',
      version='0.0.1',
      description='Utility package for thereadingmachine',
      packages=find_packages(),
      long_description=long_description,
      url='',
      author=['Michael C. J. Kao', 'Marco Garieri',
              'Luca Pozzi', 'Alberto Munisso'],
      author_email='mkao006@gmail.com',
      install_requires=[
          'pandas',
          'nltk',
          'sqlalchemy',
          'scipy',
          'scikit-learn',
          'scrapy'
      ],
      license='MIT')
