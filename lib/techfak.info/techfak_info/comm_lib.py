from email.mime.text import MIMEText
from smtplib import SMTP, SMTPException, SMTPAuthenticationError

from . import MAIL


def write_mail(subject: str, body: str, to: str) -> None:
    msg = MIMEText(body)
    msg["From"] = MAIL["from"]
    msg["Subject"] = subject

    try:
        conn = SMTP(MAIL["smtp_server"], port=MAIL["smtp_port"])
        try:
            conn.starttls()
        except SMTPException:
            # local test server does not support TLS
            if MAIL["smtp_server"] != "localhost":
                print("Could not setup TLS connection with real smtp server")
        try:
            conn.login(MAIL["smtp_user"], MAIL["smtp_passwd"])
        except (SMTPException, SMTPAuthenticationError):
            # local test server does not support login
            if MAIL["smtp_server"] != "localhost":
                print(
                    """Could not login at real smtp server, are the credentials in the
                    config file correct?"""
                )
        conn.sendmail(MAIL["smtp_sender"], to, msg.as_string())
        conn.quit()
    except ConnectionRefusedError:
        print("Connection Request refused. Could not send mail!")
