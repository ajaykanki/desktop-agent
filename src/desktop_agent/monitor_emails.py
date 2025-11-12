from O365 import Account, Message
from desktop_agent.worker.core import task, app
from tenacity import retry, stop_after_attempt, wait_fixed
from desktop_agent.settings import config
from desktop_agent.services.o365 import create_o365_account
from desktop_agent.logger import logger
import time



def authorize_user(email: str):
    """Authorizes a user and returns the user token"""

    pass


@retry(reraise=True, stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_new_mails(account: Account):
    inbox = account.mailbox().inbox_folder()
    query = inbox.new_query().equals("isRead", False)
    return list(inbox.get_messages(query=query, order_by="receivedDateTime DESC"))


def save_attachments(message: Message):
    pass


def process_message(message: Message) -> str:
    subject = message.subject
    if not subject:
        raise ValueError(
            "Subject line cannot be empty. Please provide a subject line that matches a workflow name."
        )

    if message.is_read:
        raise ValueError("Message is already read. Please mark the message as unread.")

    email = str(message.sender.address).lower()

    # TODO: Good way to trigger the appropriate workflow

    # TODO: Save attachments temporarily for triggering the workflow

    # TODO: Create a job and get the job_id

    return "something"


def monitor_emails():
    if not config.o365.validate_config():
        logger.error("Invalid configuration. Exiting.")
        exit(1)

    if not config.wmill.validate_config():
        logger.error("Invalid configuration. Exiting.")
        exit(1)

    account = create_o365_account(config.o365.model_dump())

    while True:
        try:
            mails = get_new_mails(account)
        except Exception as e:
            logger.error(e)
            time.sleep(30)
            continue

        if not mails:
            logger.info("No new emails received. Waiting...")
            time.sleep(30)
            continue

        for msg in mails:
            logger.info(
                "New email from {sender} | Subject: {subject}",
                sender=msg.sender.name,
                subject=msg.subject,
            )
            try:
                job_id = process_message(msg)
            except Exception as e:
                # Failed to create job
                logger.error(e)
                continue

            if not job_id:
                # Failed to create job
                pass

            reply = msg.reply()
            reply.body = f"Hi {msg.sender.name},Your job has been created successfully.<br><br>You can view the job flow at https://something/run/{job_id}"
            reply.send()

            logger.success("Job createds successfully! Job ID: {}", job_id)
            logger.info("Execution URL: http://localhost/run/{}", job_id)

        time.sleep(30)


if __name__ == "__main__":
    authorize_user("ajay_kanki@welspun.com")
