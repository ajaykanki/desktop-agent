EMAIL_TEMPLATES = {
    "unauthorized": {
        "subject": "[Access Denied] Unauthorized Workflow Request",
        "body": """Hi {name},<br>
            Your request was received, but you are <span style="color: red;"><b>NOT AUTHORIZED</b></span> to run this workflow.<br><br>
            If you believe this is an error or require access, please contact your administrator.<br><br>
            Thanks & Regards,<br>
            WTSL Automations
            """,
    },
    "user_not_found": {
        "subject": "[Access Denied] User not found",
        "body": """Hi {name},<br>
            Your request could not be completed because you are are <span style="color: red;"><b>NOT REGISTERED</b></span>in the system.<br><br>
            If you believe this is an error or require access, please contact your administrator.<br><br>
            Thanks & Regards,<br>WTSL Automations
            """,
    },
    "no_attachments": {
        "subject": "[Error] Missing attachments",
        "body": """Hi {name},<br>
        Your request was received, but it cannot be processed because <span style="color: red"><b>NO ATTACHMENTS<b></span> were provided.<br><br>

        Please resend your request with the necessary attachments.<br><br>
        Thanks & Regards,<br>
        WTSL Automations
        """,
    },
    "no_subject": {
        "subject": "[Error] Missing subject line. Unable to process request.",
        "body": """Hi {name},<br>
        Your request cannot be processed because the subject line is empty.<br>
        Please provide a subject line that matches a workflow name to start the workflow.<br><br>

        Thanks & Regards,<br>
        WTSL Automations
        """,
    },
}
