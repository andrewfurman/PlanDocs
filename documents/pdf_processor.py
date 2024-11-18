# pdf_processor.py : the extract text from PDF function takes in a PDF file and then extract all of the text from that PDF and preserves the table layout by limiting table columns with pipes

import io
import pdfplumber

def format_markdown_table(table):
    if not table:
        return ""

    # Replace None values with empty strings
    table = [['' if cell is None else str(cell) for cell in row] for row in table]

    # Calculate the maximum width for each column
    col_widths = [max(len(cell) for cell in col) for col in zip(*table)]

    # Format the header
    header = "| " + " | ".join(cell.ljust(width) for cell, width in zip(table[0], col_widths)) + " |"
    separator = "|" + "|".join("-" * (width + 2) for width in col_widths) + "|"

    # Format the rows
    rows = []
    for row in table[1:]:
        formatted_row = "| " + " | ".join(cell.ljust(width) for cell, width in zip(row, col_widths)) + " |"
        rows.append(formatted_row)

    # Combine all parts
    return "\n".join([header, separator] + rows) + "\n"


def extract_text_from_pdf(pdf_file):
    text = ""

    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            # Add Page number marker on its own line
            page_marker = f"\n🅿️ Start Page {page_num}\n"
            text += page_marker

            # Extract words and their positions
            words = page.extract_words()

            # Extract tables and their bounding boxes
            tables = page.extract_tables()
            table_boxes = [table.bbox for table in page.find_tables()]

            # Create a list to hold words and tables in order
            elements = []

            for word in words:
                # Check if the word is within any table
                in_table = any(
                    table_box[0] <= word['x0'] <= table_box[2] and
                    table_box[1] <= word['top'] <= table_box[3]
                    for table_box in table_boxes
                )
                if not in_table:
                    elements.append(('word', word))
                else:
                    # If it's the first word in a table, add the table
                    table_index = next(
                        i for i, table_box in enumerate(table_boxes)
                        if table_box[0] <= word['x0'] <= table_box[2] and
                           table_box[1] <= word['top'] <= table_box[3]
                    )
                    if table_index not in [e[1] for e in elements if e[0] == 'table']:
                        elements.append(('table', table_index))

            # Process elements in order
            current_line = ""
            for element_type, element in elements:
                if element_type == 'word':
                    if current_line and element['top'] != elements[elements.index((element_type, element)) - 1][1]['top']:
                        text += current_line.strip() + "\n"
                        current_line = ""
                    current_line += element['text'] + " "
                else:  # It's a table
                    if current_line:
                        text += current_line.strip() + "\n"
                        current_line = ""
                    markdown_table = format_markdown_table(tables[element])
                    text += "\n" + markdown_table + "\n"

            # Add any remaining text
            if current_line:
                text += current_line.strip() + "\n"

    return text