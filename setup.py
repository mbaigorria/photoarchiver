from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='photoarchiver',
      version='0.5',
      description='Archive your photos and files using file timestamps and geolocation.',
      url='http://github.com/mbaigorria/photoarchiver',
      author='Martín Baigorria Alonso',
      author_email='martinbaigorria@gmail.com',
      license='MIT',
      packages=['photoarchiver', 'photoarchiver.helpers'],
      install_requires=[
          'exifread',
          'reverse_geocoder',
          'tqdm',
          'requests'
      ],
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'photoarchiver = photoarchiver.__main__:main',
          ]
      },
      classifiers=(
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ),
      long_description=long_description,
      long_description_content_type='text/markdown')