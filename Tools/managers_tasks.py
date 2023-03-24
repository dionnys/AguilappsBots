from datetime import datetime




class ScheduledTask:
    def __init__(self, user_id, url, message="", notification_date=None, notification_email="", notification_number=0):
        self.user_id = user_id
        self.url = url
        self.message = message
        self.creation_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.notification_state = False
        self.notification_date = notification_date
        self.notification_email = notification_email
        self.notification_number = notification_number

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "url": self.url,
            "message": self.message,
            "creation_date": self.creation_date,
            "notification_state": self.notification_state,
            "notification_date": self.notification_date,
            "notification_email": self.notification_email,
            "notification_number": self.notification_number
        }