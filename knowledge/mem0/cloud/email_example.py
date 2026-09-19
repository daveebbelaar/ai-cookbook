from mem0 import MemoryClient
from email.parser import Parser
from dotenv import load_dotenv

load_dotenv("../.env")


# Initialize Mem0 client
client = MemoryClient()


class EmailProcessor:
    def __init__(self):
        """Initialize the Email Processor with Mem0 memory client"""
        self.client = client

    def process_email(self, email_content, user_id):
        """
        Process an email and store it in Mem0 memory

        Args:
            email_content (str): Raw email content
            user_id (str): User identifier for memory association
        """
        # Parse email
        parser = Parser()
        email = parser.parsestr(email_content)

        # Extract email details
        sender = email["from"]
        recipient = email["to"]
        subject = email["subject"]
        date = email["date"]
        body = self._get_email_body(email)

        # Create message object for Mem0
        message = {
            "role": "user",
            "content": f"Email from {sender}: {subject}\n\n{body}",
        }

        # Create metadata for better retrieval
        metadata = {
            "email_type": "incoming",
            "sender": sender,
            "recipient": recipient,
            "subject": subject,
            "date": date,
        }

        # Store in Mem0 with appropriate categories
        response = self.client.add(
            messages=[message],
            user_id=user_id,
            metadata=metadata,
            categories=["email", "correspondence"],
            version="v2",
        )

        return response

    def _get_email_body(self, email):
        """Extract the body content from an email"""
        # Simplified extraction - in real-world, handle multipart emails
        if email.is_multipart():
            for part in email.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        else:
            return email.get_payload(decode=True).decode()

    def search_emails(self, query, user_id):
        """
        Search through stored emails

        Args:
            query (str): Search query
            user_id (str): User identifier
        """
        # Search Mem0 for relevant emails
        results = self.client.search(
            query=query,
            filters={"user_id": user_id},
            categories=["email"],
            output_format="v1.1",
            version="v2",
        )

        return results

    def get_email_thread(self, subject, user_id):
        """
        Retrieve all emails in a thread based on subject

        Args:
            subject (str): Email subject to match
            user_id (str): User identifier
        """
        filters = {
            "AND": [
                {"user_id": user_id},
                {"categories": {"contains": "email"}},
                {"metadata": {"subject": {"contains": subject}}},
            ]
        }

        thread = self.client.get_all(
            version="v2", filters=filters, output_format="v1.1"
        )

        return thread


# Initialize the processor
processor = EmailProcessor()

# Example raw email
sample_email = """From: alice@example.com
To: bob@example.com
Subject: Meeting Schedule Update
Date: Mon, 15 Jul 2024 14:22:05 -0700

Hi Bob,

I wanted to update you on the schedule for our upcoming project meeting.
We'll be meeting this Thursday at 2pm instead of Friday.

Could you please prepare your section of the presentation?

Thanks,
Alice
"""

# Process and store the email
user_id = "bob@example.com"
processor.process_email(sample_email, user_id)

# Later, search for emails about meetings
meeting_emails = processor.search_emails("meeting schedule", user_id)
print(f"Found {len(meeting_emails['results'])} relevant emails")
