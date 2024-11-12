from email.message import EmailMessage
import smtplib
import os

from celery import shared_task


@shared_task()
def send_async_email_task(email_to: str, subject: str, body: dict):
    """
    Отправка email.
    """
    msg = EmailMessage()
    msg["From"] = 'SibDoski-server@yandex.ru'
    msg["To"] = email_to
    msg["Subject"] = subject

    body_html = f"""
        <html>
            <body>
                <p>{body.get('msg', 'Сообщение не указано')}</p>
                <p>Email: {body.get('email', 'Email не указан')}</p>
            </body>
        </html>
    """

    msg.set_content("Это текстовая версия сообщения", subtype='plain')
    msg.add_alternative(body_html, subtype='html')

    try:
        with smtplib.SMTP('smtp.yandex.com', 587) as server:
            server.starttls()
            server.login('SibDoski-server@yandex.ru', 'hqtfcofrmqpruxdi')
            server.send_message(msg)
    except Exception as e:
        print(f"email sending error: {e}")
        return 'error'

    return True
