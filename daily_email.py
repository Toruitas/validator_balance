import os
import base64
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)

to_email = os.environ.get('TO_EMAIL')
sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))

message = Mail(
    from_email=to_email,
    to_emails=to_email,
    subject="Steaker status is UP. Yesterday's CSV attached.",
    html_content='See CSV for earnings.'
)

with open('csvs/daily/test.csv', 'rb') as f:
    data = f.read()
    f.close()
encoded_file = base64.b64encode(data).decode()

attachedFile = Attachment(
    FileContent(encoded_file),
    FileName('test.csv'),
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