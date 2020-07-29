# PDF Content Converter

The PDF Content Converter is a tool for converting PDF text as well as structural features into a pandas dataframe.
It retrieves information about textual content, fonts, positions, character frequencies and surrounding visual PDF elements.

## How-to

* Pass the path of the PDF file which is wanted to be converted to ```PDFContentConverter```
* Call the function ```convert()```. The PDF content is then returned as a pandas dataframe.

Example call: 

    converter = PDFContentConverter(pdf)
    result = converter.convert()

An example usage is also given in ```Tester.py```.

## Output Format

The output containing the converted PDF data is stored as pandas dataframe.
The different PDF elements are stored as rows.
The dataframe contains the following columns:

* ```id```: unique identifier of the PDF element
* ```text```: text of the PDF element
* ```page```: page number, starting with 0
* ```x_0```: left x coordinate
* ```x_1```: right x coordinate
* ```y_0```: top y coordinate
* ```y_1```: bottom y coordinate
* ```pos_x```: center x coordinate
* ```pos_y```: center y coordinate
* ```abs_pos```: tuple containing a page independent representation of ```(pos_x,pos_y)``` coordinates
* ```original_font```: font as extracted by pdfminer
* ```font_name```: name of the font extracted from ```original_font```
* ```code```: font code as provided by pdfminer
* ```bold```: factor 1 indicating that a text is bold and 0 otherwise
* ```italic```: factor 1 indicating that a text is italic and 0 otherwise
* ```font_size```: size of the text in points
* ```masked```: text with numeric content substituted as #
* ```frequency_hist```: histogram of character type frequencies in a text, stored as a tuple containing percentages of textual, numerical, text symbolic and other symbols
* ```len_text```: number of characters
* ```n_tokens```: number of words
* ```tag```: tag for key-value pair extractions, indicating keys or values based on simple heuristics
* ```box```: box extracted by pdfminer Layout Analysis
* ```in_element_ids```: contains IDs of surrounding visual elements such as rectangles or lists. They are stored as a list [left, right, top, bottom]. -1 is indicating that there is no adjacent visual element.
* ```in_element```: indicates based on in_element_ids whether an element is stored in a visual rectangle representation (stored as "rectangle") or not (stored as "none").

Additionally, a dictionary is returned as a Pickle object containing the following entries,
which can be used to transform the absolute CSV coordinates:

* ```x0```: Left x page crop box coordinate
* ```x1```: Right x page crop box coordinate
* ```y0```: Top y page crop box coordinate
* ```y1```: Bottom y page crop box coordinate
* ```x0page```: Left x page coordinate
* ```x1page```: Right x page coordinate
* ```y0page```: Top y page coordinate
* ```y1page```: Bottom y page coordinate

## Project Structure

* ```PDFContentConverter.py```: contains the ```PDFContentConverter``` class for converting PDF documents.
* ```util```:
  * ```constants```: paths to input and output data, pdfminer parameters
  * ```StorageUtil```: store/load functionalities
* ```Tester.py```: Python script for testing the ```PDFContentConverter```
* ```csv```: example csv output files for tests
* ```pdf```: example pdf input files for tests

## Future Work

* We plan to adapt the ```PDFContentConverter``` for an additional direct parsing of PDF content into plain text using the pdfminer functionality.

## Acknowledgements

* This work is built on top of the pdfminer project https://github.com/pdfminer/pdfminer.six.
* Example PDFs are obtained from the ICDAR Table Recognition Challenge 2013 https://roundtrippdf.com/en/data-extraction/pdf-table-recognition-dataset/.
