# getPdfUrl.py
import requests
import io
from .pdf_processor import extract_text_from_pdf  # Update this line

def get_url_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Create a BytesIO object from the content
        pdf_file = io.BytesIO(response.content)

        # Extract text from the PDF
        text = extract_text_from_pdf(pdf_file)

        return text
    except requests.RequestException as e:
        return f"Error fetching PDF: {str(e)}"
    except Exception as e:
        return f"Error processing PDF: {str(e)}"
