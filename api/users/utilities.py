from smtplib import SMTPException
from socket import gaierror

from django.core.mail import send_mail
from django.conf import settings

assert settings.EMAIL_HOST_USER, "Missing Email Configurations"


def send_email(subject, body, recipients):
    try:
        send_mail(subject        = subject,
                  message        = body,
                  from_email     = settings.EMAIL_HOST_USER,
                  recipient_list = recipients,
                  fail_silently  = False)

    except SMTPException as err:
        raise AssertionError(err.args[0])

    except ConnectionRefusedError as err:
        raise AssertionError("Proxy configurations disabled to locate SMTP server for sending emails.")

    except gaierror:
        raise AssertionError("Unable to locate SMTP server for sending emails.")
