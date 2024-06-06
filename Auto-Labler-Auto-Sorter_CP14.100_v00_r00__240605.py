import os
import pickle
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_service():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    return service

def list_emails(service, query=''):
    # Call the Gmail API
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    return messages

def get_message(service, msg_id):
    message = service.users().messages().get(userId='me', id=msg_id).execute()
    return message

# Define your criteria for categorizing emails
def categorize_email(subject, snippet):
    if 'important' in subject.lower() or 'important' in snippet.lower():
        return '1) Important'
    elif 'urgent' in subject.lower() or 'urgent' in snippet.lower():
        return '2.1 🟢UrgentActNow'
    elif '2 min' in subject.lower() or '2 min' in snippet.lower():
        return '2.2 🟢 < 2 Min items'
    elif 'more than 2 min' in subject.lower() or 'more than 2 min' in snippet.lower():
        return '2.3 🟢 More than > 2 Min items'
    elif 'next action' in subject.lower() or 'next action' in snippet.lower():
        return '2.4 🟢 Next Actions List'
    elif 'general comms' in subject.lower() or 'general comms' in snippet.lower():
        return '3.1 🔴 General Comms (Non-team)'
    elif 'team agenda' in subject.lower() or 'team agenda' in snippet.lower():
        return '3.2 🔴 Team Agendas'
    elif 'follow up' in subject.lower() or 'follow up' in snippet.lower():
        return '4) 🩶 FollowUpTilDone'
    elif 'hold' in subject.lower() or 'hold' in snippet.lower():
        return '5.1 🩶 iHold.OthersAct'
    elif 'monitor' in subject.lower() or 'monitor' in snippet.lower():
        return '5.2 🩶 TheirTurn-iMonitorDelReg'
    elif 'calendar' in subject.lower() or 'calendar' in snippet.lower():
        return '6) Calendar'
    elif 'reminder' in subject.lower() or 'reminder' in snippet.lower():
        return '7.1 ⚫ This Week’s ReMinders'
    elif 'scheduled' in subject.lower() or 'scheduled' in snippet.lower():
        return '7.2 ⚫ SiCal'
    elif 'future reminder' in subject.lower() or 'future reminder' in snippet.lower():
        return '7.3 ⚫ Future ReMinders/Tickler'
    else:
        return '13) Other'

def auto_categorize_emails(service):
    emails = list_emails(service, query='is:unread')
    for email in emails:
        msg = get_message(service, email['id'])
        subject = msg['payload']['headers'][0]['value']
        snippet = msg['snippet']
        category = categorize_email(subject, snippet)
        print(f"Email with subject '{subject}' categorized as '{category}'")
        # Here, you can handle categorization logic like moving emails to folders or applying labels as needed

if __name__ == '__main__':
    service = get_service()
    auto_categorize_emails(service)
