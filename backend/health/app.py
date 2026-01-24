import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """
    Health check Lambda function.
    Returns a simple health status response.
    """
    logger.info("Health check requested")
    
    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,OPTIONS"
        },
        "body": json.dumps({
            "status": "healthy",
            "service": "resumetry-backend",
            "timestamp": context.aws_request_id if context else "local"
        })
    }
    
    return response

