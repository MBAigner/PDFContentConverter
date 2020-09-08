from distutils.core import setup
setup(
  name='PDFContentConverter',
  packages=['PDFContentConverter'],
  version='0.3',
  license='MIT',
  description='A tool for converting PDF text as well as structural features into a pandas dataframe. ',
  author='Michael Aigner, Florian Preis',
  # author_email='your.email@domain.com',
  url='https://github.com/MBAigner/PDFContentConverter',
  download_url='https://github.com/MBAigner/PDFContentConverter/archive/0.2.tar.gz',
  keywords=['pdf-converter', 'pdf pdf-document-processor', 'pdf-data-extraction', 'pandas', 'pandas-dataframe', 'python'],
  install_requires=[
          'pdfminer',
          'pandas',
          'numpy',
          ''
      ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7'
  ],
)