import json
import os
import requests
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        result = []
        appsheet_responses = []

        # Log received event
        logger.info("Received raw event: %s", json.dumps(event, indent=2))

        # Parse the body of the event (if it's a string)
        if "body" in event:
            try:
                event_body = json.loads(event["body"])  # Convert string to JSON
                logger.info("Parsed event body: %s", json.dumps(event_body, indent=2))
            except json.JSONDecodeError as e:
                logger.error("JSON parsing error: %s", str(e))
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid JSON in request body"})
                }
        else:
            event_body = event  # If there's no "body", use the whole event as is.

        # Extract relevant fields from each tracking event
        for tracking in event_body.get("trackings", []):
            for event_entry in tracking.get("events", []):
                extracted_data = {
                    "statusCode_exctd": event_entry.get("statusCode"),
                    "status_exctd": event_entry.get("status"),
                    "trackingNumber_exctd": event_entry.get("trackingNumber"),
                    "occurrenceDatetime_exctd": event_entry.get("occurrenceDatetime"),
                    "statusMilestone_exctd": event_entry.get("statusMilestone")
                }
                result.append(extracted_data)

                # Log extracted data
                logger.info("Extracted data: %s", json.dumps(extracted_data, indent=2))

                # Send data to AppSheet API
                appsheet_url = f"https://www.appsheet.com/api/v2/apps/{os.getenv('appsheet_app_id')}/tables/t0633/Action"
                headers = {
                    "Content-Type": "application/json",
                    "ApplicationAccessKey": os.getenv("appsheet_access_key")
                }
                payload = {
                    "Action": "Add",
                    "Properties": {"Locale": "en-US"},
                    "Rows": [
                        {
                            "tracking_id": extracted_data["trackingNumber_exctd"],
                            "status_code": extracted_data["statusCode_exctd"],
                            "status_cmb": extracted_data["status_exctd"],
                            "status_milestone": extracted_data["statusMilestone_exctd"],
                            "status_ts": extracted_data["occurrenceDatetime_exctd"]
                        }
                    ]
                }

                # Log payload
                logger.info("AppSheet payload: %s", json.dumps(payload, indent=2))

                response = requests.post(appsheet_url, headers=headers, json=payload)
                response_data = {
                    "status_code": response.status_code,
                    "response_body": response.json()
                }
                appsheet_responses.append(response_data)

                # Log AppSheet response
                logger.info("AppSheet response: %s", json.dumps(response_data, indent=2))

                response.raise_for_status()

        return {
            "statusCode": 200,
            "body": json.dumps({"extracted_data": result, "appsheet_responses": appsheet_responses}, indent=2)
        }
    except Exception as e:
        logger.error("Error: %s", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}, indent=2)
        }
