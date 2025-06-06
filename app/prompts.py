from app.logger import setup_logger

logger = setup_logger('prompts')

def generate_email_system_prompt():
    """
    Generate the system prompt for email generation
    """
    logger.debug("Generating system prompt for email")
    return """
        You are a sales professional writing a follow-up email. Start your response
        with a compelling, relevant, and concise subject line (prefixed with "Subject:").
        The subject should be personalized and attention-grabbing, based on the 
        conversation summary and company context. Then, write the email in a natural,
        conversational style with two clear paragraphs. The first paragraph should acknowledge
        the conversation and show understanding of their needs. The second paragraph should
        focus on specific next steps and solutions, and end with a clear, actionable call to
        action suggesting a follow-up meeting on Monday or Tuesday between 1pm or 2pm. 
        Sign off with "Best regards," and a blank line for the signature. Keep it concise
        and personal. Do not include any placeholders or instructions in the output.
    """

def construct_email_prompt(tone: str, contact_name: str, company_name: str, summary: str, transcript: str = None) -> str:
    """
    Constructs the prompt for email generation based on the provided parameters.
    
    Args:
        tone (str): The desired tone of the email
        contact_name (str): Name of the contact
        company_name (str): Name of the company
        summary (str): Summary of the conversation
        transcript (str, optional): Chat transcript if available
        
    Returns:
        str: Constructed prompt for email generation
    """
    logger.debug(f"Constructing email prompt for {contact_name} from {company_name}")
    
    prompt = f"""Write a {tone.lower()} follow-up email to {contact_name} from {company_name}.

Conversation Summary:
{summary}"""

    if transcript:
        logger.debug("Including transcript in prompt")
        prompt += f"\n\nChat Transcript:\n{transcript}"

    prompt += '\n\nWrite a natural email with two clear paragraphs. The first paragraph should acknowledge the conversation and show understanding. The second paragraph should focus on specific next steps. End with a clear, actionable call to action on its own line. Sign off with "Best regards," followed by a blank line for the signature.'

    logger.debug(f"Successfully constructed prompt (length: {len(prompt)})")
    return prompt

