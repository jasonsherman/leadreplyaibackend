from flask import Blueprint, jsonify, request
from app.logger import setup_logger
from app.utils import validate_email_request, generate_email_content

# Initialize logger
logger = setup_logger('routes')

main = Blueprint('main', __name__)

@main.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API is running"""
    logger.debug("Health check request received")
    return jsonify({'status': 'healthy'})

@main.route('/api/generate-email', methods=['POST'])
def generate_email():
    """
    Generate a follow-up email based on the provided parameters
    
    Expected JSON payload:
    {
        "tone": str,
        "contactName": str,
        "companyName": str,
        "summary": str,
        "transcript": str (optional)
    }
    
    Returns:
        JSON response with structured email data:
        {
            "subject": str,
            "body": str,
            "summary": str,
            "contactName": str,
            "companyName": str,
            "tone": str
        }
    """
    try:
        logger.info("Received email generation request")
        data = request.json
        logger.debug(f"Request data: {data}")

        # Validate request data
        logger.debug("Validating request data")
        validation_error = validate_email_request(data)
        if validation_error:
            logger.warning(f"Validation failed: {validation_error}")
            return jsonify({'error': validation_error}), 400

        # Generate email content
        logger.info(f"Generating email for {data['contactName']} from {data['companyName']}")
        email_response = generate_email_content(data)
        
        logger.info("Successfully generated email")
        logger.debug(f"Generated email - Subject: {email_response['subject']}, Body length: {len(email_response['body'])}")
        
        return jsonify(email_response)

    except Exception as e:
        logger.error(f"Error generating email: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to generate email'}), 500
