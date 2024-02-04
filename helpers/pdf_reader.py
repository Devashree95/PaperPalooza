import pdfplumber
from timeit import default_timer as timer


def not_within_bboxes(obj, bboxes):
    """Check if the object is in any of the table's bbox."""
    def obj_in_bbox(_bbox):
        
        """See https://github.com/jsvine/pdfplumber/blob/stable/pdfplumber/table.py#L404"""
        v_mid = (obj["top"] + obj["bottom"]) / 2
        h_mid = (obj["x0"] + obj["x1"]) / 2
        x0, top, x1, bottom = _bbox
        return (h_mid >= x0) and (h_mid < x1) and (v_mid >= top) and (v_mid < bottom)

    return not any(obj_in_bbox(__bbox) for __bbox in bboxes)




# def multiprocess_pdf_extraction(path,glob):
#     for file in glob:
def get_text_content(etd_file):    
    with pdfplumber.open(etd_file) as pdf:
        no_of_pages=(len(pdf.pages))
        images = pdf.images
        text_content = ""
        for i in range((no_of_pages)):
            bboxes=[]
            page = pdf.pages[i]
            tables = page.find_tables(table_settings={
                        "vertical_strategy": "lines",
                        "horizontal_strategy": "lines",
                        "explicit_vertical_lines": page.curves + page.edges,
                        "explicit_horizontal_lines": page.curves + page.edges,
                    })
            bboxes = [
                table.bbox
                for table in tables
            ]

            for imageObj in images:
                if imageObj['page_number'] == i+1:
                    bounding_box = (imageObj['x0'], imageObj['top'], imageObj['x1'], imageObj['bottom'])
                    bboxes.append(bounding_box)

            # print((page.filter(lambda obj: not_within_bboxes(obj, bboxes)).extract_text()))
            text_content += str(page.extract_text())
        return text_content

# start = timer()

# process(path,glob_list)
# # multiprocessing.freeze_support()
# # process_pool = multiprocessing.Pool()
# # func = partial(process, path)
# # process_pool.map(func, glob_list)
# # process_pool.close()
# # process_pool.join()
# print("That took "+ str(timer()-start))