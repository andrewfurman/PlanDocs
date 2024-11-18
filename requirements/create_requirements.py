# This function will create all of the requirements for a document section. 

#  It will pass a prompt that includes the Summary of the Document, The Document Section Text, and the document section title.

# It will then request an array of requirements from the ChatGPT OpenAI API in order to write the requirements for the requirements database table.  This will include the section_id, section_title, requirement description, workstream, page_number. The custom prompt field will not be generated.

import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from openai import OpenAI
from documents.documents_model import DocumentSection
from requirements.requirements_model import Requirement

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def create_requirements(document_section_id: int):
    # Set up database connection
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Get the document section contents, summary, and title
        document_section = session.query(DocumentSection).get(document_section_id)
        if not document_section:
            raise ValueError(f"No document section found with id {document_section_id}")
        
        section_text = document_section.document_text
        document_summary = document_section.document.summary
        section_title = document_section.title

        # Prepare the ChatGPT API request

        payload = {
            "model": "gpt-4o-mini",  # or whichever model you prefer
            "messages": [
                {
                    "role": "system",
                    "content": """
                    
                    Prompt:
                    You are a Medicare subject matter expert responsible for thoroughly reviewing CMS (Centers for Medicare & Medicaid Services) manuals in PDF format and extracting claims requirements from these documents. These requirements will directly inform the development of business requirements for a claims processing system. Given the critical nature of compliance, accuracy and completeness are paramount—any errors or omissions may result in severe penalties for non-compliance with CMS regulations. You are expected to meticulously follow the outlined instructions to ensure precision.
                    Instructions:

                    Extract Section Information from TOC: At the beginning of each CMS manual, locate the Table of Contents. You are required to extract the section numbers and names and input them into the first column of the provided Excel template.

                    Extract Requirements from Each Section: Carefully review each section and subsection of the CMS manual, ensuring that you capture every single line and paragraph verbatim. Enter the exact text of each requirement into the second column of the Excel file, corresponding directly to the section from which it was extracted.

                    Map to Claims Sub-processes: For every requirement extracted, you must map it to one of the following claims sub-processes and enter this in the third column of the Excel sheet:

                    Claims intake EDI (Electronic Data Interchange)
                    Pre-adjudication (e.g., eligibility verification, duplicate checks)
                    Benefits (determination of covered services and member financial responsibilities)
                    Pricing (based on fee schedules or contracted provider rates)
                    Claims Editing (accuracy, completeness, and compliance with policies)
                    Claims Payment (generation of payment advice and disbursement of funds)
                    Encounters Submission (reporting patient visits/services)
                    Member/Provider Correspondence (communications such as Explanation of Benefits or claims disputes)
                    Recoveries/Reconsiderations/Adjustments (handling overpayments, underpayments, or claim adjustments)

                    Record Page Numbers: For every requirement, note the exact page number from the CMS manual in the fourth column of the Excel file. This ensures traceability and allows for easy verification.
                    Output: The final output must align with the provided sample Excel structure, with the following fields fully populated for each extracted requirement:

                    Section Number
                    Section Name
                    Extracted Requirement
                    Claims Sub-process
                    Page Number
                    Important Considerations:
                    Thoroughness: Every line and paragraph must be reviewed and extracted; no content should be skipped.
                    Mapping Accuracy: It is crucial to accurately assign each requirement to its relevant claims sub-process, as misclassification could lead to significant compliance risks.
                    Focus on Quality: The task's priority is precision, not speed. Any mistake in this process could potentially expose the organization to regulatory penalties.
                    
                    """
                },
                {
                    "role": "user",
                    "content": f"Document Summary: {document_summary}\nSection Title: {section_title}\nSection Text: {section_text}"
                }
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "requirements",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "requirements": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "section_id": {
                                            "type": "string",
                                            "description": "Unique identifier for the section within the document. An example would be '1.1'"
                                        },
                                        "section_title": {
                                            "type": "string",
                                            "description": "Title of the section containing the requirement."
                                        },
                                        "requirement_description": {
                                            "type": "string",
                                            "description": "Detailed description of the requirement extracted from the document section."
                                        },
                                        "workstream": {
                                            "type": "string",
                                            "description": "The workstream or category to which this requirement belongs."
                                        },
                                        "page_number": {
                                            "type": "integer",
                                            "description": "The page number in the document where this requirement is found."
                                        }
                                    },
                                    "required": ["section_id", "section_title", "requirement_description", "workstream", "page_number"],
                                    "additionalProperties": False
                                },
                                "description": "List of requirements extracted from the document section."
                            }
                        },
                        "required": ["requirements"],
                        "additionalProperties": False
                    }
                }
            }
        }

        # Send request to ChatGPT API
        response = client.chat.completions.create(**payload)

        # Extract the requirements from the response
        requirements_data = json.loads(response.choices[0].message.content)['requirements']

        # Delete existing requirements for this document_section_id
        session.query(Requirement).filter_by(document_section_id=document_section_id).delete()

        # Update the database with new requirements
        for req_data in requirements_data:
            new_requirement = Requirement(
                document_section_id=document_section_id,
                section_id=req_data['section_id'],
                section_title=req_data['section_title'],
                requirement_description=req_data['requirement_description'],
                workstream=req_data['workstream'],
                page_number=req_data['page_number']
            )
            session.add(new_requirement)

        session.commit()
        return f"Generated {len(requirements_data)} requirements for document section {document_section_id}"

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()