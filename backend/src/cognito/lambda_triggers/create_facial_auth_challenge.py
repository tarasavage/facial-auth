import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event: dict, context: dict) -> dict:
    logger.debug(f"Received event: {json.dumps(event, indent=2)}")

    if event["request"]["challengeName"] == "CUSTOM_CHALLENGE":
        event["response"].update(
            {
                "publicChallengeParameters": {"challengeType": "FACE_AUTH"},
                "privateChallengeParameters": {"validationType": "FACE_AUTH"},
                "challengeMetadata": "FACE_AUTHENTICATION",
            }
        )
        logger.info(f"Updated event: {json.dumps(event, indent=2)}")
    return event
