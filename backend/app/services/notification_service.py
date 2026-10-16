import os
from abc import ABC, abstractmethod
from typing import Optional

class NotificationProvider(ABC):
    @abstractmethod
    def send_notification(self, recipient_id: str, email: Optional[str], phone: Optional[str], message: str) -> bool:
        pass

class MockNotificationProvider(NotificationProvider):
    def send_notification(self, recipient_id: str, email: Optional[str], phone: Optional[str], message: str) -> bool:
        # In a real environment, this hooks into SMTP, SendGrid, Twilio, or AWS SNS
        print("=" * 60)
        print("NOTIFICATION DISPATCH LOG:")
        print(f"To User ID: {recipient_id}")
        if email:
            print(f"Email sent: {email} -> '{message}'")
        if phone:
            print(f"SMS sent: {phone} -> '{message}'")
        print("=" * 60)
        return True

def get_notification_provider() -> NotificationProvider:
    return MockNotificationProvider()
