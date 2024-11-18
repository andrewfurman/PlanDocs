# the create_compressed_document_gpt(document_id int) function will use the OpenAI API to create a compressed document from the full text of the document.

# this function will use the full_contents field of the document table to create a compressed document using the OpenAI API. This function will send chunks of the full document in 20 page segments.  This will be done by scanning the full_contents field for the page delimiters shown as "🅿️ Start Page 1" "🅿️ Start Page 2" and so on.  It will use these delimiters to split the document into chunks of 20 page segements and request an updated summary of each page in the chunk. The chunk returned will keep the "🅿️ Page 1 Summary: " "🅿️Page 2 Summary: " and so on.

from sqlalchemy import create_engine, true
from sqlalchemy.orm import sessionmaker
import os
import re
import json
import sys
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from documents.documents_model import Document

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def split_into_pages(full_contents):
    if not full_contents:
        return []
    # Use positive lookbehind to keep the page markers
    pages = re.split(r'(?=🅿️ Start Page \d+)', full_contents)
    # Remove empty first element if it exists
    if pages and not pages[0].strip():
        pages.pop(0)
    return pages

def create_segments(pages, segment_size):
    return [pages[i:i + segment_size] for i in range(0, len(pages), segment_size)]

def get_page_summaries(segment, base_page_num):
    # Extract page numbers from the segment text to use in the summary
    page_numbers = [int(num) for num in re.findall(r'🅿️ Start Page (\d+)', ''.join(segment))]
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a dilligent document research expert tasked with creating concise 50-word summaries for each page of a document."
            },
            {
                "role": "user",
                "content": f"Create a 50-word summary for each of these pages, This is an exerpt from a larger document that needs to be summarized. Please preserve the origianl page numbers found in this document text:\n\n{' '.join(segment)}"
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "page_summaries",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "page_summaries": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "page_number": {
                                        "type": "integer",
                                        "description": "The page number being summarized, please refer to the page number in the original text sent indicated by '🅿️ Start Page 20' '🅿️ Start Page 21' and so on. do not indicate the number of pages in this request (which is a subset of the original document), but instead use the original document."
                                    },
                                    "table_of_contents": {
                                        "type": "boolean",
                                        "description": "True if the page contains entirely table of contents, false if it contains any other content. If there is some table of contents, and some addtional content, then this will be false."
                                    },
                                    "content_continued_from_previous_page": {
                                        "type": "boolean",
                                        "description": "True if the page continues from the previous page, false if it does not. To determine if the content is continued from the previous page, see if there is a sentance continued from the previous page, or if the content on this page is related to the previous page content."
                                    },
                                    "start_of_new_section": {
                                        "type": "boolean",
                                        "description": "True if this page is the start of a new section of the document that has content that can be analyzed separately from previous pages. False if this page is a continuation of a scetion of content from previous pages."
                                    },
                                    "page_summary": {
                                        "type":"string",
                                        "description": "A 50 word detailed summary of the content on the page free of filler words."
                                    }
                                },
                                "required": ["page_number", "table_of_contents", "content_continued_from_previous_page", "start_of_new_section", "page_summary"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["page_summaries"],
                    "additionalProperties": False
                }
            }
        }
    }

    # Get the response from OpenAI
    response = client.chat.completions.create(**payload)

    # Now try to parse the JSON
    print("Attempting to parse JSON from response from OpenAI...")
    parsed_response = json.loads(response.choices[0].message.content)

    return parsed_response

def create_compressed_document_gpt(document_id, pages_per_segment=5):
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        print(f"\n[DEBUG] Starting compression for document_id: {document_id}")
        document = session.query(Document).filter(Document.id == document_id).first()
        if not document or not document.full_contents:
            print("[DEBUG] Document not found or empty")
            return "Error: Document not found or empty."

        print(f"[DEBUG] Found document with title: {document.title}")
        pages = split_into_pages(document.full_contents)
        print(f"[DEBUG] Split document into {len(pages)} pages")
        
        segments = create_segments(pages, pages_per_segment)
        print(f"[DEBUG] Created {len(segments)} segments of {pages_per_segment} pages each")
        
        # Initialize list to store all summaries
        all_summaries = []
        
        print("[DEBUG] Starting parallel processing of segments")
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(get_page_summaries, segment, segment_index * pages_per_segment)
                for segment_index, segment in enumerate(segments)
            ]
            
            # Collect all summaries into one list
            for future_index, future in enumerate(futures):
                print(f"[DEBUG] Processing result from future {future_index + 1}/{len(futures)}")
                result = future.result()
                print(f"[DEBUG] Got {len(result['page_summaries'])} summaries from segment {future_index + 1}")
                all_summaries.extend(result['page_summaries'])
        
        print(f"[DEBUG] Total summaries collected: {len(all_summaries)}")
        
        # Create final JSON structure
        compressed_json = {
            'document_id': document_id,
            'total_pages': len(pages),
            'summaries': sorted(all_summaries, key=lambda x: x['page_number'])
        }
        
        # Convert to string and log
        json_string = json.dumps(compressed_json, indent=2)
        print("\n[DEBUG] Final JSON string to save:")
        print(json_string)
        
        print("\n[DEBUG] Document state before update:")
        print(f"compressed_document: {document.compressed_document}")
        
        # Use setattr to set the column value
        setattr(document, 'compressed_document', json_string)
        
        print("\n[DEBUG] Document state after setattr:")
        print(f"compressed_document: {document.compressed_document}")
        
        print("\n[DEBUG] Attempting to commit to database...")
        session.commit()
        
        # Verify the save
        session.refresh(document)
        print(f"compressed_document: {document.compressed_document}")
        
        return f"Success: Created compressed document for ID {document_id}"
    except Exception as e:
        print(f"\n[DEBUG] Error occurred: {str(e)}")
        print(f"[DEBUG] Error type: {type(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        session.rollback()
        return f"Error: {str(e)}"
    finally:
        print("[DEBUG] Closing session")
        session.close()