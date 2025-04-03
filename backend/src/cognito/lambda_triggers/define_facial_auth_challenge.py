import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event: dict, context: dict) -> dict:
    logger.debug(f"Received event: {json.dumps(event, indent=2)}")

    try:
        session: list[dict] = event["request"]["session"]
        logger.debug(f"Session data: {json.dumps(session, indent=2)}")

        logger.info(f"User: {event['request'].get('userAttributes', {}).get('email', 'Unknown')}")

        response: dict = event["response"]
        if len(session) == 0:
            logger.info("Initial authentication attempt - issuing CUSTOM_CHALLENGE")

            response.update(failAuthentication=False, issueTokens=False, challengeName="CUSTOM_CHALLENGE",)

        elif (
            len(session) == 1
            and session[0]["challengeName"] == "CUSTOM_CHALLENGE"
            and session[0]["challengeResult"] is True
        ):
            logger.info("Challenge completed successfully - issuing tokens")

            response.update(failAuthentication=False, issueTokens=True)

        else:
            logger.error("Authentication failed - invalid session state")
            logger.debug(f"Last challenge name: {session[-1].get('challengeName')}")
            logger.debug(f"Last challenge result: {session[-1].get('challengeResult')}")

            response.update(failAuthentication=True, issueTokens=False)

        logger.debug(f"Returning response: {json.dumps(event['response'], indent=2)}")

        return event

    except Exception as e:
        logger.error(f"Error in define auth challenge: {str(e)}", exc_info=True)
        event["response"].update(failAuthentication=True, issueTokens=False)
        return event
