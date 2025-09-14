from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from tqdm import tqdm  # progress bar library

# Authenticate with stored token.json
creds = Credentials.from_authorized_user_file(
    'token.json',
    ['https://mail.google.com/']
)
service = build('gmail', 'v1', credentials=creds)

def get_or_create_label(service, label_name):
    """Get label ID if exists, else create it"""
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    for label in labels:
        if label['name'] == label_name:
            return label['id']

    # Create label if not found
    label_body = {
        'name': label_name,
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show'
    }
    new_label = service.users().labels().create(userId='me', body=label_body).execute()
    print(f"Created label: {label_name}")
    return new_label['id']

def list_all_messages(service, query):
    """Return all message IDs matching the query"""
    message_ids = []
    req = service.users().messages().list(userId='me', q=query, maxResults=500)
    while req:
        resp = req.execute()
        msgs = resp.get('messages', [])
        message_ids.extend([m['id'] for m in msgs])
        req = service.users().messages().list_next(previous_request=req, previous_response=resp)
    return message_ids

def filter_unlabeled_messages_bulk(service, message_ids, label_id, batch_size=500):
    """Filter messages that do not already have the label using batch get"""
    unlabeled = []
    for msg_id in tqdm(message_ids, desc="Filtering unlabeled", leave=False):
        msg = service.users().messages().get(userId='me', id=msg_id, format='metadata').execute()
        existing_labels = msg.get('labelIds', [])
        if label_id not in existing_labels:
            unlabeled.append(msg_id)
    return unlabeled

def process_messages_in_batches(service, message_ids, label_id, batch_size=1000):
    """Apply label and remove INBOX in batches with progress bar"""
    total_messages = len(message_ids)
    print(f"Total messages to process (unlabeled): {total_messages}")
    if total_messages == 0:
        return

    processed_count = 0
    for i in tqdm(range(0, total_messages, batch_size), desc="Processing batches"):
        batch = message_ids[i:i+batch_size]
        service.users().messages().batchModify(
            userId='me',
            body={
                'ids': batch,
                'addLabelIds': [label_id],
                'removeLabelIds': ['INBOX']
            }
        ).execute()
        processed_count += len(batch)
        tqdm.write(f"Processed {processed_count}/{total_messages} emails")

def main():
    rules = {
        "alerts@axisbank.com": "Communications/Financials/Bank/Axis",
        "bytebytego@substack.com": "Blog/ByteByteGo",
        "*@linkedin.com": "Social/LinkedIn"
        # add more as needed
    }

    for sender, label in rules.items():
        print(f"\nProcessing {sender} → {label}")
        label_id = get_or_create_label(service, label)
        message_ids = list_all_messages(service, f"from:{sender}")
        message_ids = filter_unlabeled_messages_bulk(service, message_ids, label_id)
        process_messages_in_batches(service, message_ids, label_id)

    print("✅ All emails processed.")

if __name__ == "__main__":
    main()
