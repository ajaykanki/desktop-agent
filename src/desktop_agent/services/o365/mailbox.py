from pathlib import Path
from O365 import Account
import logging

logger = logging.getLogger(__name__)


# TODO: Add delete_files to rpa-toolkit
def delete_files(files: str | Path | list[str] | list[Path]):
    if isinstance(files, str):
        path = Path(files)
        path.unlink(missing_ok=True)

    elif isinstance(files, Path):
        files.unlink(missing_ok=True)

    elif isinstance(files, list[Path]):
        for file_ in files:
            file_.unlink(missing_ok=True)

    elif isinstance(files, list[str]):
        for file_ in files:
            path = Path(file_)
            path.unlink(missing_ok=True)
    return


class Mailbox:
    def __init__(self):
        pass

    @staticmethod
    def reply(
        account: Account,
        *,
        to: str | list[str],
        conversation_id: str,
        body: str | None = None,
        subject: str | None = None,
        cc: str | list[str] | None = None,
        attachments: str | list[str] | list[Path] | None = None,
        delete_attachments: bool = False,
    ):
        if not account:
            raise ValueError("Account is required.")

        if not to:
            raise ValueError("To/Reciepient address is required.")

        if not conversation_id:
            raise ValueError("Conversation ID is required.")

        failed = False

        try:
            inbox = account.mailbox().inbox_folder()
            query = inbox.new_query().equals("conversationId", conversation_id)

            msg = inbox.get_message(query=query)

            if not msg:
                raise ValueError(
                    f"Message with conversation_id: {conversation_id} not found."
                )

            _reply = msg.reply()

            if subject:
                _reply.subject = subject

            if body:
                _reply.body = body

            if to:
                _reply.to.add(to)

            if cc:
                _reply.cc.add(cc)

            if attachments:
                _reply.attachments.add(attachments)

            result = _reply.send()

            if result:
                logging.info(f"Reply message sent successfully: {result}")

            return result
        except Exception as e:
            logger.error(f"Failed to reply email message: {e}")
            raise e
        finally:
            if not attachments:
                return

            if failed:
                return

            if not delete_attachments:
                return

            delete_files(attachments)

    @staticmethod
    def send_message(
        account: Account,
        *,
        to: str | list[str],
        body: str | None = None,
        subject: str | None = None,
        cc: str | list[str] | None = None,
        attachments: str | list[str] | None = None,
    ):
        if not to:
            raise ValueError("To/Reciepient address is required.")

        try:
            inbox = account.mailbox().inbox_folder()
            msg = inbox.new_message()
            msg.to.add(to)

            if subject:
                msg.subject = subject

            if body:
                msg.body = body

            if cc:
                msg.cc.add(cc)

            if attachments:
                msg.attachments.add(attachments)

            result = msg.send()
            if result:
                logging.info(f"Email message sent successfully: {result}")

            return result
        except Exception as e:
            logger.error(f"Failed to send email message: {e}")
            raise e
