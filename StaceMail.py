#!/usr/bin/python

import httplib2
from email.mime.text import MIMEText
import base64

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from apiclient import errors


def authenticate(force_refresh=False):
    # Path to the client_secret.json file downloaded from the Developer Console
    client_secret_file_name = 'client_secret.json'
    gmail_cred_store = 'gmail_auth_store.json'

    # Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
    oauth_scope = 'https://mail.google.com/'

    # Location of the credentials storage file
    storage = Storage(gmail_cred_store)

    # Start the OAuth flow to retrieve credentials
    flow = flow_from_clientsecrets(client_secret_file_name, scope=oauth_scope)
    http = httplib2.Http()

    # Try to retrieve credentials from storage or run the flow to generate them
    credentials = storage.get()
    if credentials is None or credentials.invalid or force_refresh:
        credentials = run(flow, storage, http=http)

    # Authorize the httplib2.Http object with our credentials
    http = credentials.authorize(http)

    # Build the Gmail service from discovery
    gmail_service = build('gmail', 'v1', http=http)

    return gmail_service


def get_threads(gmail_service, q):
    # Retrieve a page of threads
    threads = gmail_service.users().threads().list(userId='me', q=q).execute()
    return threads


def get_thread(service, user_id, thread_id):
    try:
        thread = service.users().threads().get(userId=user_id, id=thread_id).execute()
        return thread
    except errors.HttpError, error:
        print 'An error occurred: %s' % error


def create_message(sender, to, subject, message_text, thread_id=None, rpl_msg_id_raw=None):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_msg = {}
    if thread_id is not None and rpl_msg_id_raw is not None:
        message['In-Reply-To'] = rpl_msg_id_raw
        message['References'] = rpl_msg_id_raw
        message['subject'] = 'Re: ' + subject
        raw_msg['threadId'] = thread_id
    raw_msg['raw'] = base64.urlsafe_b64encode(message.as_string())
    return raw_msg


def create_draft(service, user_id, message_body):
    try:
        message = {'message': message_body}
        draft = service.users().drafts().create(userId=user_id, body=message).execute()

        # print 'Draft id: %s\nDraft message: %s' % (draft['id'], draft['message'])

        return draft
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
        return None


def send_message(service, user_id, message_body):
    try:
        message = (service.users().messages().send(userId=user_id, body=message_body).execute())
        print 'sent Message Id: %s' % message['id']
        return message
    except errors.HttpError, error:
        print 'An error occurred: %s' % error


def main():
    print('authenticating...'),
    gmail_service = authenticate()
    print "success"

    threads = get_threads(gmail_service, 'StaceMail')

    to = 'marcher@srcity.org'
    if "threads" not in threads.keys():
        message = create_message('mmadink@gmail.com', to, 'StaceMail', 'test with python')
        send_message(gmail_service, 'me', message)

    # Print ID for each thread
    else:
        for thread in threads['threads']:
            # print thread.keys()
            thread_id = thread['id']

            t_thread = get_thread(gmail_service, 'me', thread_id)
            messages = t_thread['messages']
            msg_count = len(messages)
            last_msg = messages[msg_count - 1]
            msg_id_raw = None
            for header in last_msg['payload']['headers']:
                if header['name'].lower() == 'message-id':
                    msg_id_raw = header['value']
            if msg_id_raw is None:
                print "Couldn't reply to thread: %s, Message-id is None" % thread_id
                continue

            print "thread id: %s" % thread_id
            print "message id: %s" % msg_id_raw
            print "msg_count: %s" % msg_count

            message = create_message('mmadink@gmail.com', to, 'StaceMail', 'test with python', thread_id, msg_id_raw)
            #create_draft(gmail_service, 'me', message)
            send_message(gmail_service, 'me', message)
            print ''
        # break;

if __name__ == '__main__':
    main()