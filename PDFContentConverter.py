import pandas as pd
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextLine, LTTextBox, LTImage, \
    LTFigure, LTLine, LTRect, LTCurve
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import re
import numpy as np
from util import constants


class PDFContentConverter(object):

    def __init__(self, pdf):
        self.pdf = pdf
        self.font_size = None
        self.font_name = None
        self.box_id = -1
        self.rect_boxes = []
        self.plot_boxes = []
        self.res = None
        self.media_boxes = None

    def parse_document(self):
        self.res = []  # result set
        n = 0  # page count
        self.media_boxes = dict()  # media coordinate dictionary
        pdf = open(self.pdf, "rb")
        pdf_parser = PDFParser(pdf)
        pdf_document = PDFDocument(pdf_parser)
        la_params = LAParams(detect_vertical=True)
        if constants.USE_CUSTOM_PDF_PARAMETERS:
            la_params = LAParams(detect_vertical=constants.DEFAULT_DETECT_VERTICAL,
                                 line_overlap=constants.DEFAULT_LINE_OVERLAP,
                                 line_margin=constants.DEFAULT_LINE_MARGIN,
                                 word_margin=constants.DEFAULT_WORD_MARGIN,
                                 char_margin=constants.DEFAULT_CHAR_MARGIN,
                                 boxes_flow=constants.DEFAULT_BOXES_FLOW)

        if pdf_document.is_extractable:
            resource_manager = PDFResourceManager()
            page_aggregator = PDFPageAggregator(resource_manager,
                                                laparams=la_params)
            page_interpreter = PDFPageInterpreter(resource_manager,
                                                  page_aggregator)
            pages = PDFPage.create_pages(pdf_document)

            for page in pages:
                page_interpreter.process_page(page)
                layout = page_aggregator.get_result()
                crop_box = page.cropbox
                page_box = page.mediabox
                self.media_boxes[n] = {"x0": crop_box[0], "y0": crop_box[1],
                                       "x1": crop_box[2], "y1": crop_box[3],
                                       "x0page": page_box[0], "y0page": page_box[1],
                                       "x1page": page_box[2], "y1page": page_box[3]}
                self.box_id = -1
                res = self.get_objects(layout._objs, self.res, n, self.media_boxes)
                n += 1

            return self.res, self.media_boxes

    def convert(self):
        res, media_boxes = self.parse_document()
        if len(res) == 0:
            return None, None
        lines = pd.DataFrame(res)
        lines.columns = ["id", "page", "text",
                         "x_0", "x_1", "y_0", "y_1",
                         "pos_x", "pos_y", "abs_pos",
                         "original_font", "font_name", "code", "bold", "italic", "font_size",
                         "masked", "frequency_hist",
                         "len_text", "n_tokens",
                         "tag", "box"]
        lines = lines.apply(lambda x: self.create_surrounding_element_features(x, self.rect_boxes, min=3),
                            axis=1)

        return {"content": lines,
                "media_boxes": media_boxes}

    def get_objects(self, layout_objs, res, n, media_boxes):
        page_height = media_boxes[n]["y1page"]
        for obj in layout_objs:
            if isinstance(obj, LTTextLine):
                y1 = page_height - obj.y1
                y0 = page_height - obj.y0
                pos_x = (obj.x0 + obj.x1) / 2
                pos_y = (y0 + y1) / 2

                self.font_size = abs(y1 - y0)
                text = obj.get_text()
                rgb = self.get_rgb(text)
                text = self.clean_text(text)
                masked_text = self.mask_text(text)
                tag = self.get_tag(text)

                self.font_name = obj._objs[0].fontname
                font_name_original = self.font_name
                code = ""
                if "+" in self.font_name:
                    parts = self.font_name.split("+")
                    code = parts[0]
                    self.font_name = parts[1]
                italic = 1 if "Italic" in self.font_name else 0
                bold = 1 if "Bold" in self.font_name else 0
                self.font_name = self.font_name.replace("+", "").replace("-", "").\
                    replace("Bold", "").replace("Italic", "").replace(",", "")

                if len(text.replace(" ", "")) != 0:  # filter empty text
                    res.append(
                        [
                            len(res), n, obj.get_text().replace('\n', ' '),
                            obj.x0, obj.x1,
                            y0, y1,
                            pos_x, pos_y,
                            (pos_x, page_height - pos_y - page_height * num_pages),
                            font_name_original,
                            self.font_name, code, bold, italic,
                            self.font_size,
                            masked_text, rgb,
                            len(text), len(text.split(" ")),
                            tag, self.box_id
                        ]
                    )
            elif isinstance(obj, LTTextBox):
                self.box_id = self.box_id + 1
                self.get_objects(obj._objs, res, n, media_boxes)
            else:
                type = ""
                if isinstance(obj, LTRect) or isinstance(obj, LTCurve) or isinstance(obj, LTLine):
                    type = "rectangle" if obj.height > 10 and obj.width > 10 else "line"
                elif isinstance(obj, LTFigure):
                    type = "figure"
                elif isinstance(obj, LTImage):
                    type = "image"
                self.add_visual_elements(type, n, obj, page_height)

        return res

    def clean_text(self, text):
        text = text.replace("\\x0", " ").replace('\n', ' ').replace('\r', ' ')
        text = re.sub(" +", " ", text)
        text = text.strip()
        return text

    def get_tag(self, text):
        if len(text) > 0 and text[-1] == ":":
            tag = "key"
        else:
            tag = "value"
        return tag

    def mask_text(self, text):
        text = re.sub("\d+", "#", text)
        text = text.lower()
        return text

    def get_rgb(self, text):
        len_all = len(text)
        len_text = len(re.findall("[A-Za-zÄÖÜäöü]", text))
        len_digits = len(re.findall("[0-9]", text))
        len_text_symbols = len(re.findall("[,\.!\?](\s|$)", text))
        len_symbols = len_all - len_text - len_digits - len_text_symbols
        if len_all > 0:
            return (len_text / len_all,          # text
                    len_digits / len_all,        # digits
                    len_symbols / len_all,       # symbols
                    len_text_symbols / len_all)  # text symbols
        else:
            return (0, 0, 0, 0)

    def add_visual_elements(self, type, num_pages, obj, page_height):
        if type == "line":
            # add single line
            self.rect_boxes.append([type, num_pages, round(obj.x0), round(obj.x1),
                                    round(page_height - obj.y1), round(page_height - obj.y0)])

        elif type == "rectangle":
            type = "line"
            # bottom
            self.rect_boxes.append([type, num_pages,
                                    round(obj.x0), round(obj.x1),
                                    round(page_height - obj.y0), round(page_height - obj.y0+1)])
            # left
            self.rect_boxes.append([type, num_pages,
                                    round(obj.x0-1), round(obj.x0),
                                    round(page_height - obj.y1), round(page_height - obj.y0)])
            # right
            self.rect_boxes.append([type, num_pages,
                                    round(obj.x1), round(obj.x1+1),
                                    round(page_height - obj.y1), round(page_height - obj.y0)])
            # top
            self.rect_boxes.append([type, num_pages,
                                    round(obj.x0), round(obj.x1),
                                    round(page_height - obj.y1-1), round(page_height - obj.y1)])

        elif type == "image" or type == "figure":
            self.plot_boxes.append([type, num_pages,
                                    obj.x0, obj.x1, page_height - obj.y1, page_height - obj.y0])

    def create_surrounding_element_features(self, location, elements, min):
        lines = self.get_surrounding_lines(location, elements)
        location["in_element_ids"] = lines
        location["in_element"] = "rectangle" if lines.count(-1) <= 4-min else "none"
        return location

    def get_surrounding_rectangles(self, location, elements):
        rectangles = list(filter(lambda x: x[0] == "rectangle" and x[1] == location["page"],
                                 elements))
        rect_ids = []
        for i, rect in enumerate(rectangles):
            if location["x_0"] >= rect[2] and location["x_1"] <= rect[3] and \
                    location["y_0"] >= rect[5] and location["y_1"] <= rect[4]:
                rect_ids.append(i)
        return rect_ids if rect_ids != [] else None

    def get_surrounding_lines(self, location, elements):
        lines = list(filter(lambda x: x[0] == "line" and x[1] == location["page"],
                            elements))
        left_dist = np.inf
        left_id = -1
        right_dist = np.inf
        right_id = -1
        bottom_dist = np.inf
        bottom_id = -1
        top_dist = np.inf
        top_id = -1

        for i, line in enumerate(lines):
            # top
            if line[2] <= location["x_0"] and location["x_1"] <= line[3] and location["y_1"] >= line[4]:
                dist = location["y_1"] - line[4]
                if dist < top_dist:
                    top_dist = dist
                    top_id = line[4]
            # bottom
            if line[2] <= location["x_0"] and location["x_1"] <= line[3] and location["y_0"] <= line[5]:
                dist = line[5] - location["y_0"]
                if dist < bottom_dist:
                    bottom_dist = dist
                    bottom_id = line[5]
            # left
            if location["x_0"]+2 >= line[2] and line[5] >= location["y_0"] and location["y_1"] >= line[4]:
                dist = location["x_0"] - line[2]
                if dist < left_dist:
                    left_dist = dist
                    left_id = line[2]
            # right
            if location["x_1"]-2 <= line[3] and line[5] >= location["y_0"] and location["y_1"] >= line[4]:
                dist = line[3] - location["x_1"]
                if dist < right_dist:
                    right_dist = dist
                    right_id = line[3]

        ids = [left_id, right_id, top_id, bottom_id]
        return ids
