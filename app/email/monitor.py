import asyncio
from typing import TypedDict, Any
from pydantic import BaseModel
from app.logging import log
from app.exceptions import EmailTriggerError
from .wmill_client import Windmill
from .mailbox import Mailbox
from .templates import EMAIL_TEMPLATES
from O365 import Account, Message


class MSGraphCredentials(BaseModel):
    client_id: str
    client_secret: str
    tenant_id: str
    main_resource: str


class EmailProcessingResult(BaseModel):
    job_id: str
    runnable: dict[str, Any]


class Attachment(TypedDict):
    name: str
    content: str


class EmailMonitor:
    POLLING_INTERVAL = 30  # seconds

    def __init__(self, credentials: MSGraphCredentials, wmill_client: Windmill):
        self.credentials = (credentials.client_id, credentials.client_secret)
        self.tenant_id = credentials.tenant_id
        self.main_resource = credentials.main_resource
        self.wmill = wmill_client
        self.account = self._create_o365_account()
        self.is_running = False

    def _create_o365_account(self) -> Account:
        account = Account(
            credentials=self.credentials,
            tenant_id=self.tenant_id,
            auth_flow_type="credentials",
            main_resource=self.main_resource,
        )
        if not account.is_authenticated:
            log.info("Account not authenticated. Attempting to authenticate.")
            success = account.authenticate()
            if not success:
                raise ValueError(
                    "Failed to authenticate account with provided credentials."
                )
        return account

    def _get_new_emails(self, folder: str | None = "Inbox") -> list[Message]:
        inbox = self.account.mailbox().get_folder(folder_name=folder)
        query = inbox.new_query().equals("isRead", False)
        return list(inbox.get_messages(query=query, order_by="receivedDateTime DESC"))

    def _raise_trigger_error(self, key: str) -> None:
        template = EMAIL_TEMPLATES.get(key)
        raise EmailTriggerError(
            subject=template.get("subject"), body=template.get("body")
        )

    def _authorize_user(self, email: str) -> tuple[str, list[dict[str, Any]]]:
        """
        Authorizes a user by checking if they exist and retrieves their runnables.
        """
        if not self.wmill.user_exists(email):
            self._raise_trigger_error("user_not_found")

        token = self.wmill.create_token_impersonate(email)
        runnables = self.wmill.get_all_runnables(token)

        if not runnables:
            self._raise_trigger_error("unauthorized")

        return token, runnables

    def runnable_requires_b64_attachments(self, properties: dict[str, Any]) -> bool:
        """
        Recursively checks if any property in the schema contains "contentEncoding" and equals "base64".
        """
        if not isinstance(properties, dict):
            return False

        if "contentEncoding" in properties:
            if properties["contentEncoding"] == "base64":
                return True

        for value in properties.values():
            if isinstance(value, dict) and self.runnable_requires_b64_attachments(
                value
            ):
                return True

        return False

    def prepare_attachments(self, msg: Message) -> list[Attachment]:
        msg.attachments.download_attachments()
        attachments: list[Attachment] = []
        for attachment in msg.attachments:
            if attachment.is_inline:
                continue
            attachments.append({"name": attachment.name, "content": attachment.content})

        return attachments

    def get_best_matching_workflow(self, subject: str, runnables: dict):
        """Get the best matching workflow based on the subject and runnables."""
        subject_lower = subject.lower()
        subject_tokens = subject_lower.split(" ")
        subject_tokens_set = set(subject_tokens)

        for wf in runnables:
            path_tokens = wf["path"].replace("_", " ").replace("/", " ").lower().split()
            path_tokens_set = set(path_tokens)

            matches = subject_tokens_set & path_tokens_set
            if len(matches) >= 2:
                return wf

        return None

    def process_message(self, msg: Message) -> EmailProcessingResult:
        """
        Process an email message to trigger the appropriate workflow.
        """
        subject = msg.subject
        if not subject:
            self._raise_trigger_error("no_subject")

        email = str(msg.sender.address).strip().lower()
        token, runnables = self._authorize_user(email)
        runnable = self.get_best_matching_workflow(subject, runnables)

        if not runnable:
            self._raise_trigger_error("unauthorized")

        log.info("Authorized runnable: {}", runnable.get("path"))

        require_attachments = "input_files" in runnable.get("schema").get("properties")
        log.info("Attachments required: {}", require_attachments)

        if require_attachments:
            if not msg.has_attachments:
                self._raise_trigger_error("no_attachments")

            # Check if the flow requires base64 attachments or list of file paths
            input_files_schema = (
                runnable.get("schema").get("properties").get("input_files")
            )
            is_b64 = self.runnable_requires_b64_attachments(input_files_schema)

            if is_b64:
                # Trigger the worfkloww directly without saving the attachments to disk
                log.info("Preparing attachments...")
                attachments = self.prepare_attachments(msg)

                # Check if the flow requires a single attachment or a list of base64 attachments
                if input_files_schema.get("type") == "string":
                    attachments = attachments[0].get("content")

                resp = self.wmill.post(
                    runnable.get("endpoint_async"),
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "input_files": attachments,
                        "is_email_triggered": True,
                        "conversation_id": msg.conversation_id,
                    },
                )
                return EmailProcessingResult(job_id=resp.text, runnable=runnable)

            # This means that the flow requires a list of paths.
            # First save the attachments to temp dir and then trigger the workflow
            # TODO: Implement this

        # This would mean that the flow does not require input_files as param, so trigger the flow without attachments
        resp = self.wmill.post(
            runnable.get("endpoint_async"),
            headers={"Authorization": f"Bearer {token}"},
            json={
                "is_email_triggered": True,
                "conversation_id": msg.conversation_id,
            },
        )
        return EmailProcessingResult(job_id=resp.text, runnable=runnable)

    async def check_new_emails(self) -> None:
        """
        Check for new emails and process them if found.
        """
        messages = self._get_new_emails()
        if not messages:
            log.info("No new emails found.")
            return

        for msg in messages:
            log.info(
                "New email received from {sender} | Subject: {subject}",
                sender=msg.sender.address,
                subject=msg.subject,
            )
            try:
                result = self.process_message(msg)
                await self._send_success_response(msg, result.job_id, result.runnable)
            except EmailTriggerError as e:
                log.error(e.subject)
                e.body = e.body.replace("{name}", msg.sender.name)
                Mailbox.reply_to_msg(
                    msg,
                    subject=e.subject,
                    body=e.body,
                )
            except Exception as e:
                log.error(f"Unexpected error processing email: {str(e)}")
                await self._send_error_response(msg, str(e))

    async def _send_success_response(
        self, msg: Message, job_id: str, runnable: dict[str, Any]
    ) -> None:
        execution_url = f"{self.wmill.instance_url}/run/{job_id}"
        path = runnable.get("path")
        summary = runnable.get("summary")
        description = runnable.get("description")
        workspace = runnable.get("workspace")

        subject = f"Workflow {path} triggered successfully."
        body = f"""
            Hi {msg.sender.name},<br>
            Your request has been received and the workflow <span style="color: rgb(12, 100, 192);"><b>{runnable.get("path")}</b></span> has been triggered successfully.<br><br>
            You can view the execution details, logs, and real-time status using the link below:<br>👉
            <a href="{execution_url}">Click here to view the execution details</a><br><br>

            <b>Workflow details:</b><br>
            Name: {summary}<br>
            Path: {path}<br>
            Description: {description}<br>
            Workspace: {workspace}<br><br>

            <span style="background-color: yellow"><b>Note:</b></span> If you did not intend to trigger this workflow or incorrect workflow was triggered, please reply to this email with the subject <span style="color: red"><b>"STOP"</b></span> to cancel the workflow.
            <br><br>

            Thanks & Regards,<br>
            WTSL Automations
        """
        Mailbox.reply_to_msg(msg, subject=subject, body=body)
        log.info("Job created successfully! Job ID: {}", job_id)
        log.info("Execution URL: {}", execution_url)

    async def _send_error_response(self, msg: Message, error_message: str) -> None:
        error_subject = "[Error] Unable to process your request"
        error_body = f"""
            Hi {msg.sender.name},<br>
            We encountered an unexpected error while processing your request.<br><br>

            Error message: {error_message}<br><br>

            Thanks & Regards,<br>
            WTSL Automations
        """
        Mailbox.reply_to_msg(msg, subject=error_subject, body=error_body)

    async def start(self) -> None:
        self.is_running = True
        log.info(
            "Starting email monitoring (check interval: {}s)", self.POLLING_INTERVAL
        )
        while self.is_running:
            try:
                await self.check_new_emails()
                log.info(
                    f"Waiting for {self.POLLING_INTERVAL}s before checking again..."
                )
                await asyncio.sleep(self.POLLING_INTERVAL)
            except Exception as e:
                log.error(f"Error in email monitoring loop: {str(e)}")
                await asyncio.sleep(self.POLLING_INTERVAL)

    async def stop(self) -> None:
        """
        Stop the email monitoring loop.
        """
        self.is_running = False
        log.info("Stopping email monitoring")
