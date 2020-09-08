from PDFContentConverter import PDFContentConverter
from util import constants
from util import StorageUtil

# test file
pdf = "eu-001.pdf"
file = constants.PDF_PATH + pdf

# convert PDF
converter = PDFContentConverter(file)
result = converter.convert()  # dictionary containing text and media boxes
df = converter.pdf2pandas()  # equivalent to result["content"]
text = converter.pdf2text()  # equivalent to result["text"]
media_boxes = converter.get_media_boxes()  # equivalent to result["media_boxes"]
n_pages = converter.get_page_count()  # equivalent to result["page_count"]

# store results
csv_file = constants.CSV_PATH + StorageUtil.replace_file_type(pdf, "csv")
df.to_csv(csv_file, sep=";", index=0)
StorageUtil.save_object(result["media_boxes"], constants.CSV_PATH, StorageUtil.cut_file_type(pdf))
