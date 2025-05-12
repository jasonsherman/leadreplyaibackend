import os
import re
from openai import OpenAI
from app.logger import setup_logger
from typing import Dict, Any, Optional, TypedDict

logger = setup_logger('utils')

class EmailResponse(TypedDict):
    subject: str
    body: str
    summary: str
    contactName: str
    companyName: str
    tone: str

def get_openai_client():
    """
    Initialize and return OpenAI client
    """
    try:
        logger.debug("Initializing OpenAI client with OpenRouter API")
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        logger.debug("OpenAI client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        raise

def call_openai(client, system_prompt, prompt):
    """
    Call OpenAI API to generate content based on the provided prompts
    
    Args:
        client: OpenAI client instance
        system_prompt (str): System prompt for the AI
        prompt (str): User prompt for the AI
        
    Returns:
        str: Generated content
    """
    try:
        logger.debug("Calling OpenAI API with system prompt and user prompt")
        logger.debug(f"System prompt length: {len(system_prompt)}")
        logger.debug(f"User prompt length: {len(prompt)}")
        
        completion = client.chat.completions.create(
            extra_body={},
            model="deepseek/deepseek-prover-v2:free",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        response = completion.choices[0].message.content
        logger.debug(f"Successfully received response from OpenAI API (length: {len(response)})")
        return response
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        raise

def validate_email_request(data: Dict[str, Any]) -> Optional[str]:
    """
    Validate the email generation request data
    
    Args:
        data (Dict[str, Any]): Request data to validate
        
    Returns:
        Optional[str]: Error message if validation fails, None if validation passes
    """
    logger.debug("Starting email request validation")
    
    required_fields = ['tone', 'contactName', 'companyName', 'summary']
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return f'Missing required field: {field}'
    
    # Validate tone
    if not isinstance(data['tone'], str) or not data['tone'].strip():
        logger.warning("Invalid tone: must be a non-empty string")
        return 'Tone must be a non-empty string'
    
    # Validate contact name
    if not isinstance(data['contactName'], str) or not data['contactName'].strip():
        logger.warning("Invalid contact name: must be a non-empty string")
        return 'Contact name must be a non-empty string'
    
    # Validate company name
    if not isinstance(data['companyName'], str) or not data['companyName'].strip():
        logger.warning("Invalid company name: must be a non-empty string")
        return 'Company name must be a non-empty string'
    
    # Validate summary
    if not isinstance(data['summary'], str) or not data['summary'].strip():
        logger.warning("Invalid summary: must be a non-empty string")
        return 'Summary must be a non-empty string'
    
    # Validate transcript if provided
    if 'transcript' in data and not isinstance(data['transcript'], str):
        logger.warning("Invalid transcript: must be a string if provided")
        return 'Transcript must be a string if provided'
    
    logger.debug("Email request validation passed successfully")
    return None

def parse_email_response(response_text: str, form_data: Dict[str, Any]) -> EmailResponse:
    """
    Parse the email response into a structured format
    
    Args:
        response_text (str): Raw email response text
        form_data (Dict[str, Any]): Original form data
        
    Returns:
        EmailResponse: Structured email response
    """
    logger.debug("Parsing email response")
    
    # Extract subject
    subject_match = re.search(r'Subject:\s*(.*?)(?:\n|$)', response_text)
    subject = subject_match.group(1).strip() if subject_match else 'Follow-up on our conversation'
    logger.debug(f"Extracted subject: {subject}")
    
    # Extract body
    body_match = re.search(r'(?:Hi|Hello|Dear).*?(?:Best regards,|$)', response_text, re.DOTALL)
    body = body_match.group(0).strip() if body_match else response_text
    logger.debug(f"Extracted body length: {len(body)}")
    
    # Construct response
    response = {
        'subject': subject,
        'body': body,
        'summary': form_data['summary'],
        'contactName': form_data['contactName'],
        'companyName': form_data['companyName'],
        'tone': form_data['tone']
    }
    
    logger.debug("Successfully parsed email response")
    return response

def generate_email_content(data: Dict[str, Any]) -> EmailResponse:
    """
    Generate email content using OpenAI
    
    Args:
        data (Dict[str, Any]): Request data containing email parameters
        
    Returns:
        EmailResponse: Structured email response
    """
    try:
        logger.debug("Starting email content generation")
        from app.prompts import generate_email_system_prompt, construct_email_prompt
        
        # Get OpenAI client
        logger.debug("Getting OpenAI client")
        client = get_openai_client()
        
        # Get prompts
        logger.debug("Generating system prompt")
        system_prompt = generate_email_system_prompt()
        
        logger.debug("Constructing user prompt")
        user_prompt = construct_email_prompt(
            tone=data['tone'],
            contact_name=data['contactName'],
            company_name=data['companyName'],
            summary=data['summary'],
            transcript=data.get('transcript')
        )
        
        # Generate email
        logger.debug("Calling OpenAI to generate email content")
        generated_email = call_openai(client, system_prompt, user_prompt)
        
        logger.debug(f"Successfully generated email content (length: {len(generated_email)})")
        
        # Parse the response
        return parse_email_response(generated_email, data)
        
    except Exception as e:
        logger.error(f"Error generating email content: {str(e)}")
        raise

