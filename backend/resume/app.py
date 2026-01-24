import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """
    Resume processing Lambda function.
    Handles POST /api/resume and GET /api/resume/{id}
    """
    logger.info(f"Event: {json.dumps(event)}")
    
    http_method = event.get("httpMethod", event.get("requestContext", {}).get("http", {}).get("method", ""))
    path = event.get("path", "")
    path_parameters = event.get("pathParameters") or {}
    
    # CORS headers
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
    }
    
    # Handle OPTIONS request for CORS preflight
    if http_method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": headers,
            "body": ""
        }
    
    # Handle GET request
    if http_method == "GET":
        resume_id = path_parameters.get("id", "unknown")
        logger.info(f"Getting resume with ID: {resume_id}")
        
        # TODO: Implement actual database lookup
        response_body = {
            "id": resume_id,
            "message": "Resume retrieved successfully",
            "data": {
                "id": resume_id,
                "status": "processed",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
        
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(response_body)
        }
    
    # Handle POST request
    elif http_method == "POST":
        try:
            body = json.loads(event.get("body", "{}"))
            logger.info(f"Processing resume: {json.dumps(body)}")
            
            # TODO: Implement actual resume processing logic
            # This is a placeholder response
            response_body = {
                "message": "Resume processed successfully",
                "data": {
                    "id": context.aws_request_id if context else "local-id",
                    "status": "processing",
                    "created_at": "2024-01-01T00:00:00Z"
                }
            }
            
            return {
                "statusCode": 201,
                "headers": headers,
                "body": json.dumps(response_body)
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request body: {str(e)}")
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Invalid JSON in request body"})
            }
        except Exception as e:
            logger.error(f"Error processing resume: {str(e)}")
            return {
                "statusCode": 500,
                "headers": headers,
                "body": json.dumps({"error": "Internal server error"})
            }
    
    # Method not allowed
    else:
        return {
            "statusCode": 405,
            "headers": headers,
            "body": json.dumps({"error": f"Method {http_method} not allowed"})
        }

