from __future__ import print_function
from apiclient.discovery import build
from apiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools
from base64 import b64decode
import boto3, json, httplib2, os

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
client_kms = boto3.client('kms')
credentials = os.environ["KMS_KEY"]
response = client_kms.decrypt(CiphertextBlob=b64decode(credentials))['Plaintext']
info = json.loads(response)
client_id = info['client_id']
client_secret = info['client_secret']
refresh_token = info['refresh_token']

credentials = client.GoogleCredentials(None, 
    client_id, 
    client_secret,
    refresh_token,
    None,
    "https://accounts.google.com/o/oauth2/token",
    'my-user-agent')
    
http = credentials.authorize(httplib2.Http())
service = build('gmail', 'v1', http=http, cache_discovery=False)
query = 'is:unread'

def lambda_handler(event, context):
    # Call the Gmail API
    try:
        response = service.users().messages().list(userId='me',
                                               q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId='me', q=query,pageToken=page_token).execute()
            messages.extend(response['messages'])

        unread_messages = messages
    except errors.HttpError, error:
        print ('An error occurred: %s' % error)
    
    for unread in unread_messages:
        msg_labels = {'removeLabelIds': ['UNREAD'] }
        try:
            message = service.users().messages().modify(userId='me', id=unread['id'],
                                                    body=msg_labels).execute()

            label_ids = message['labelIds']

            print ('Message ID: %s - With Label IDs %s' % (unread['id'], label_ids))
       
        except errors.HttpError, error:
            print ('An error occurred: %s' % error)

    
    # TODO implement
    return ''

