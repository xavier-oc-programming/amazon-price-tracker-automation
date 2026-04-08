import smtplib

from config import PRODUCT_NAME, PRODUCT_URL, TARGET_PRICE, SMTP_PORT


class EmailNotifier:
    """Sends a price-drop email alert via SMTP."""

    def __init__(self, smtp_address: str, sender: str, password: str, recipient: str):
        self._smtp_address = smtp_address
        self._sender = sender
        self._password = password
        self._recipient = recipient

    def send_alert(self, current_price: float) -> bool:
        """
        Send a price-drop alert email.

        Args:
            current_price: the price that triggered the alert.

        Returns:
            True if the email was sent successfully, False otherwise.
        """
        subject = "Amazon Price Alert!"
        body = (
            f"Price dropped to {current_price:.2f} EUR — "
            f"below your target of {TARGET_PRICE:.2f} EUR!\n\n"
            f"Product : {PRODUCT_NAME}\n"
            f"Link    : {PRODUCT_URL}"
        )
        message = f"Subject:{subject}\n\n{body}"

        try:
            with smtplib.SMTP(self._smtp_address, port=SMTP_PORT) as connection:
                connection.starttls()
                connection.login(user=self._sender, password=self._password)
                connection.sendmail(
                    from_addr=self._sender,
                    to_addrs=self._recipient,
                    msg=message.encode("utf-8"),
                )
            return True
        except smtplib.SMTPAuthenticationError:
            raise ValueError("SMTP authentication failed — check your app password in .env.")
        except smtplib.SMTPException as exc:
            raise RuntimeError(f"Failed to send email: {exc}") from exc
