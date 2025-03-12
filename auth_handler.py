import os
import json
import logging
from lambda_function import lambda_handler as main_lambda_handler  # Import the main Lambda function

# Configure logging for CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Set logging level to INFO

def lambda_handler(event, context):
    try:
        # Extract the Bearer token from headers
        headers = event.get("headers", {})
        auth_header = headers.get("authorization", "")

        # Retrieve the expected token from environment variable
        expected_token = os.getenv("ship24_bearer_token")

        # Log incoming request
        logger.info("Received request: %s", json.dumps(event, indent=2))

        # Validate Authorization header
        if not auth_header.startswith("Bearer "):
            logger.warning("Unauthorized request - Missing Bearer token")
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Unauthorized - No Bearer Token"})
            }

        # Extract the actual token
        provided_token = auth_header.split("Bearer ")[1]

        # Verify the token
        if provided_token != expected_token:
            logger.warning("Forbidden request - Invalid Bearer token")
            return {
                "statusCode": 403,
                "body": json.dumps({"error": "Forbidden - Invalid Bearer Token"})
            }

        # Log successful authentication
        logger.info("Bearer token validated successfully. Forwarding request to main Lambda function.")

        # If the token is valid, forward the event to the main handler
        return main_lambda_handler(event, context)

    except Exception as e:
        logger.error("Error in authentication: %s", str(e), exc_info=True)  # Logs full traceback
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error"})
        }
