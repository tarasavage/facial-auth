import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

EXPECTED_VERIFICATION_ANSWER = "face_verified"


def lambda_handler(event: dict, context: dict) -> dict:
    logger.debug(f"Received event: {json.dumps(event, indent=2)}")

    event["response"]["answerCorrect"] = event["request"]["challengeAnswer"] == EXPECTED_VERIFICATION_ANSWER

    return event
