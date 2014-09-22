#!/usr/bin/python

#TODO: run with PowerShell
#   pip install --upgrade google-api-python-client
#   pip install python-gflags
#   python StaceMail.py

import httplib2
import base64
import csv

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from email.mime.text import MIMEText
from apiclient import errors


def main():
    print('authenticating...'),
    gmail_service = authenticate(force_refresh=False)
    print "success"

    # If as_reply=None it will try to send emails as a reply but if it can't it will send it as a new thread
    # If as_reply=True it will only send emails that it can send as a reply
    # If as_reply=False it will send all emails as new threads
    send_to_email_list(service=gmail_service, as_reply=None)


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


def create_message(sender, to, cc, bcc, subject, message_text, thread_id=None, rpl_msg_id_raw=None):
    message = MIMEText(message_text, 'html')
    message['from'] = sender
    message['to'] = to
    message['cc'] = cc
    message['bcc'] = bcc
    message['subject'] = subject
    raw_msg = {}
    if thread_id is not None and rpl_msg_id_raw:
        message['In-Reply-To'] = rpl_msg_id_raw
        message['References'] = rpl_msg_id_raw
        #message['subject'] = 'Re: ' + subject # gmail strips off the 'Re: ' for some reason.  Kind of annoying.
        raw_msg['threadId'] = thread_id
    raw_msg['raw'] = base64.urlsafe_b64encode(message.as_string())
    return raw_msg


def get_last_email_id_in_thread(service, thread_id):
    thread = get_thread(service, 'me', thread_id)
    messages = thread['messages']
    msg_count = len(messages)
    last_msg = messages[msg_count - 1]
    msg_id_raw = None
    for header in last_msg['payload']['headers']:
        if header['name'].lower() == 'message-id':
            msg_id_raw = header['value']
    return msg_id_raw


def send_message(service, user_id, message_body):
    try:
        message = (service.users().messages().send(userId=user_id, body=message_body).execute())
        print 'sent Message Id: %s' % message['id']
        return message
    except errors.HttpError, error:
        print 'An error occurred: %s' % error


def send_to_email_list(service, as_reply=None):
    # get email list
    list_headers = None
    list_lines = []
    with open('email_list.csv', 'r') as email_list_file:
        reader = csv.reader(email_list_file, delimiter=',', quotechar='"')
        for row in reader:
            # first row should be headers
            if list_headers is None:
                list_headers = row
            else:
                list_lines.append(row)

    # get template
    template = open('email_template.html', 'r').read()

    # render template for each line in the email list
    for list_line in list_lines:
        # 0-4 should be (from,to,cc,bcc,subject) respectively
        email_from = list_line[0]
        email_to = list_line[1]
        email_cc = list_line[2]
        email_bcc = list_line[3]
        email_subject = list_line[4]
        # if there isn't at least one address to send to ignore this line
        if email_to == "" and email_cc == "" and email_bcc == "":
            continue

        # render the template by replacing $ColumnName$ with the respective row value
        email_body = template
        for h_index in range(0, len(list_headers)):
            header = list_headers[h_index]
            value = list_line[h_index]
            email_body = email_body.replace('$%s$' % header, value)

        # variables for replying
        thread_id = None
        rpl_msg_id = None

        # if it should be sent as a reply, go figure out thread_id and rpl_msg_id, otherwise they'll be left empty
        if as_reply or as_reply is None:
            q = 'subject:%s to:%s' % (email_subject, email_to)
            threads = get_threads(service, q)
            if "threads" not in threads.keys():
                if as_reply:
                    print "Couldn't find thread with query (%s). Skipping this line." % q
                    continue
                else:
                    print "Couldn't find thread with query (%s). Sending as original message." % q
            else:
                if len(threads['threads']) != 1:
                    print "Warning, found multiple threads (count=%s) for query (%s). Replying to the last one" \
                          % (len(threads['threads']), q)
                thread_id = threads['threads'][0]['id']
                rpl_msg_id = get_last_email_id_in_thread(service, thread_id)

        #build and send the message
        message = create_message(
            email_from, email_to, email_cc, email_bcc, email_subject, email_body, thread_id, rpl_msg_id)
        send_message(service, 'me', message)


if __name__ == '__main__':
    main()