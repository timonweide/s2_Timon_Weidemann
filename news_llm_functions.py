import cohere
import json
from datetime import date
import requests
from fpdf import FPDF
from fpdf.enums import XPos, YPos


### Create prompt to GDELT parameter transformation

def get_gdelt_params(key, user_prompt):

    # Initialize Cohere client
    cohere_client = cohere.ClientV2(key)

    # Save the date for today
    today = date.today().strftime("%Y%m%d")

    # Define the system parameters
    system_prompt = f"""
    The user will write a text asking for news about a topic during a period.
    Extract the information necessary to populate this json object:
    {{
    "query": X,
    "startdate": X,
    "enddate": X
    }}
    The query should include a certain action (e.g. "terror" or "protest") and region (e.g. "france" or "paris"). It is intended for the GDELT API.
    The startdate and enddate should be in the format YYYYMMDD. Remember that today is {today}.
    If the information is not present, return "N/A".
    Respond only with the json object.
    """

    # Check if model input is string
    if not isinstance(user_prompt, str):
        user_prompt = str(user_prompt)

    # Get the model response
    raw_response = cohere_client.chat(
        messages = [
        {
            'role': 'system',
            'content': system_prompt  
        }, 
        {
            'role': 'user',
            'content': user_prompt
        }
        ],
        model='command-r-plus'
    )

    # Save the response
    response_text = raw_response.message.content[0].text

    # Check if response format is correct
    if '```json\n' in response_text:
        response_text_clean = response_text.split('```json\n')[1].split('\n```')[0].strip()
        try:
            response_json = json.loads(response_text_clean)
        except Exception:
            return response_text_clean
    else:
        try:
            response_json = json.loads(response_text)
        except Exception:
            return response_text
    
    # Check if the response JSON contains N/A's
    if response_json['query'] == "N/A":
        return "Query not found"
    if response_json['startdate'] == "N/A" and response_json['enddate'] == "N/A":
        response_json['enddate'] = str(int(today) - 1)
        response_json['startdate'] = str(int(response_json['enddate']) - 7)
    if response_json['startdate'] == "N/A":
        response_json['startdate'] = str(int(response_json['enddate']) - 7)
    if response_json['enddate'] == "N/A":
        response_json['enddate'] = str(int(today) - 1)

    # Check if the response JSON dates are valid
    if response_json['enddate'] == today:
        response_json['enddate'] = str(int(today) - 1)
    if int(response_json['enddate']) < int(response_json['startdate']):
        response_json['startdate'] = str(int(response_json['enddate']) - 7)

    # Return the response
    response = response_json
    return response


### Create GDELT parameter to GDELT articles query

def get_gdelt_articles(gdelt_params):

    # Extract variables parameters
    query = gdelt_params['query']
    startdate = gdelt_params['startdate']
    enddate = gdelt_params['enddate']

    # Save API attributes
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }

    # Save API parameters
    params = {
        "query": f"{query}",
        "startdatetime": f"{startdate}000000",
        "enddatetime": f"{enddate}000000",
        "mode": "artlist",
        "format": "json",
        "maxrecords": 50,
        "sort": "hybridrel"
    }

    # Get the API response
    raw_response = requests.get(url, params=params, headers=headers)

    # Check if API call is working and response format is valid and return the response
    if raw_response.status_code == 200:
        try:
            response = json.loads(raw_response.text)
        except Exception:
            response = raw_response.text
        return response
    else:
        return raw_response.status_code


### Create GDELT articles to summary transformation

def get_summary(key, user_prompt, gdelt_articles):

    # Initialize Cohere client
    cohere_client = cohere.ClientV2(key)

    # Define the system parameters
    system_prompt = f"""
    The user will give you a list of articles from GDELT including the URL, Date and Title.
    The user has previously asked:
    {user_prompt}
    Respond with a brief summary responding to the users previous question.
    Base your response only on the information from the given articles.
    Recommend the user between 1 and 5 most relevant articles including the URLs and titles. Translate the titles to English if necessary.
    Respond only with the summary and recommended articles.
    """

    # Check if model input is string
    if not isinstance(gdelt_articles, str):
        gdelt_articles = str(gdelt_articles)

    # Get the model response
    raw_response = cohere_client.chat(
        messages = [
        {
            'role': 'system',
            'content': system_prompt  
        }, 
        {
            'role': 'user',
            'content': gdelt_articles
        }
        ],
        model='command-r-plus'
    )

    # Check if the response is valid and return the response
    try:
        response = raw_response.message.content[0].text
    except Exception:
        response = raw_response
    return response


### Create PDF generation function for summary download

def generate_pdf(user_prompt, summary):
    
    # Initialize PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Set up PDF header
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, "World News Summarizer", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)
    
    # Add user prompt
    pdf.set_font("Helvetica", style="I", size=12)
    pdf.multi_cell(0, 10, user_prompt.encode('latin-1', 'replace').decode('latin-1'))
    pdf.ln(10)

    # Add summary
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, summary.encode('latin-1', 'replace').decode('latin-1'))
    
    # Return the PDF as a bytes buffer
    pdf_buffer = bytes(pdf.output())
    return pdf_buffer
