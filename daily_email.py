import os
from sys import exit
import base64
from datetime import datetime, date, timedelta, timezone
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)

to_email = os.environ.get('TO_EMAIL')
sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))



now_utc = datetime.now(timezone.utc)
today = now_utc.date()
yesterday = today - timedelta(days = 1)

try:
    with open(f'csvs/daily/{yesterday}.csv', 'rb') as f:
        data = f.read()
        f.close()
    attach_file = True
    body_content = f"The staking server is up, and there is 1 attachment for today, {today}."
except FileNotFoundError as e:
    print(f"Yesterday's file 'csvs/daily/{yesterday}.csv' not found. Proceeding without attachment.")
    attach_file = False
    body_content = f"The staking server is up, but has no attachment for today, {today}."

message = Mail(
    from_email=to_email,
    to_emails=to_email,
    subject="Staker status is UP.",
    html_content=body_content
)

if attach_file:
    encoded_file = base64.b64encode(data).decode()

    attachedFile = Attachment(
        FileContent(encoded_file),
        FileName(f'{yesterday}.csv'),
        FileType('.csv'),
        Disposition('attachment')
    )
    message.attachment = attachedFile

try:
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e)