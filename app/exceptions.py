class EmailTriggerError(Exception):
    def __init__(self, subject: str, body: str):
        self.subject = subject
        self.body = body
        super().__init__(self.subject, self.body)

    def to_dict(self):
        return {
            "subject": self.subject,
            "body": self.body,
        }
