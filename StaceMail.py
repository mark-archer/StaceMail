#!/usr/bin/python

import httplib2 
from email.mime.text import MIMEText
import base64

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run


def authenticate():
	# Path to the client_secret.json file downloaded from the Developer Console
	CLIENT_SECRET_FILE = 'client_secret.json'

	# Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
	OAUTH_SCOPE = 'https://mail.google.com/'

	# Location of the credentials storage file
	STORAGE = Storage('gmail.storage')

	# Start the OAuth flow to retrieve credentials
	flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
	http = httplib2.Http()

	# Try to retrieve credentials from storage or run the flow to generate them
	credentials = STORAGE.get()
	if credentials is None or credentials.invalid:
	  credentials = run(flow, STORAGE, http=http)

	# Authorize the httplib2.Http object with our credentials
	http = credentials.authorize(http)

	# Build the Gmail service from discovery
	gmail_service = build('gmail', 'v1', http=http)

	return gmail_service

def get_threads(gmail_service, subject):

	q = 'subject:%s' % subject

	# Retrieve a page of threads
	threads = gmail_service.users().threads().list(userId='me',q=q).execute()

	return threads

def create_message(sender, to, subject, message_text, thread_id=None):
	message = MIMEText(message_text)
	message['to'] = to
	message['from'] = sender
	message['subject'] = subject
	if thread_id:
		message['threadId'] = thread_id
	return {'raw': base64.urlsafe_b64encode(message.as_string())}

def create_draft(service, user_id, message_body):
  try:
    message = {'message': message_body}
    draft = service.users().drafts().create(userId=user_id, body=message).execute()

    print 'Draft id: %s\nDraft message: %s' % (draft['id'], draft['message'])

    return draft
  except errors.HttpError, error:
    print 'An error occurred: %s' % error
    return None

#def create_drafts(gmail_service, threads):
	
gmail_service = authenticate()
threads = get_threads(gmail_service, 'stacemail')

# Print ID for each thread
if threads['threads']:
  for thread in threads['threads']:
    print thread.keys()
    #print 'Thread ID: %s; To: %s' % (thread['id'], thread['to'])

aMsg = create_message('mmadink@gmail.com','mmadink@gmail.com','stacemail', 'test with python')
create_draft(gmail_service, 'me', aMsg)

