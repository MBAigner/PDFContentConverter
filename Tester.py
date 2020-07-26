from PDFContentConverter import PDFContentConverter
from util import constants
from util import StorageUtil

# convert PDF
pdf = "eu-001.pdf"
file = constants.PDF_PATH + pdf
converter = PDFContentConverter(file)
result = converter.convert()

# store results
csv = constants.CSV_PATH + StorageUtil.replace_file_type(pdf, "csv")
result["content"].to_csv(csv, sep=";")
StorageUtil.save_object(result["media_boxes"], constants.CSV_PATH, StorageUtil.cut_file_type(pdf))
