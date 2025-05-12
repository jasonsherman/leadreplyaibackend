from flask import Blueprint, jsonify, request
from app.logger import setup_logger


# Initialize logger
logger = setup_logger('routes')

main = Blueprint('main', __name__)


@main.route('/health', methods=['GET'])
def health_check():
    logger.debug("Health check request received")
    return jsonify({'status': 'healthy'})
