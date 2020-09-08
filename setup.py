from distutils.core import setup

with open('README.rst') as f:
    long_description = f.read()
print(long_description)
setup(
  name='PDFContentConverter',
  packages=['PDFContentConverter', 'PDFContentConverter.util'],
  version='0.7',
  license='MIT',
  description='A tool for converting PDF text as well as structural features into a pandas dataframe. ',
  long_description=long_description,
  author='Michael Aigner, Florian Preis',
  # author_email='your.email@domain.com',
  url='https://github.com/MBAigner/PDFContentConverter',
  download_url='https://github.com/MBAigner/PDFContentConverter/archive/v0.3.tar.gz',
  keywords=['pdf-converter', 'pdf pdf-document-processor', 'pdf-data-extraction', 'pandas', 'pandas-dataframe', 'python'],
  install_requires=[
          'pdfminer==20191125',
          'pandas',
          'numpy',
          ''
      ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7'
  ],
)
