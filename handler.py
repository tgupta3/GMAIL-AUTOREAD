from __future__ import print_function
from apiclient.discovery import build
from apiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools
from base64 import b64decode
import boto3, json, httplib2, os, sys, time


class Gmail():
    
    def __init__(self,credentials,query='is:unread',time_buffer=2):
        self.credentials = credentials
        self.batch_size = 999
        self.client_kms = boto3.client('kms')
        self.service = self.__build_service()
        self.query = self.__build_query(query,time_buffer)
    
    
    def __build_query(self,query,time_buffer):
        time_current = int(time.time())
        time_past = time_current - 3600*time_buffer
        return (query + ' AND before:' + str(time_past)) 
    
    def __build_service(self):
        id,secret,token = self.__get_creds()
        client_credentials =  client.GoogleCredentials(
            None,
            id,
            secret,
            token,
            None,
            "https://accounts.google.com/o/oauth2/token",
            'my-user-agent'
        )
        http = client_credentials.authorize(httplib2.Http())
        return build('gmail', 'v1', http=http, cache_discovery=False)
       
        
    def __get_creds(self):
        client_kms = boto3.client('kms')
        response = client_kms.decrypt(CiphertextBlob=b64decode(self.credentials))['Plaintext']
        info = json.loads(response)
        client_id = info['client_id']
        client_secret = info['client_secret']
        refresh_token = info['refresh_token']
        return client_id,client_secret,refresh_token
        
    def list_unread(self,userid='me'):
        try:
            response = self.service.users().messages().list(userId=userid,
                                                       q=self.query).execute()
            messages = []
            if 'messages' in response:
              messages.extend(response['messages'])
        
            while 'nextPageToken' in response:
              page_token = response['nextPageToken']
              response = self.service.users().messages().list(userId=userid, q=self.query,
                                                 pageToken=page_token).execute()
              messages.extend(response['messages'])
        
            unread_messages = messages
        except errors.HttpError, error:
            print ('An error occurred: %s' % error)    
        return unread_messages


    def mark_read(self,unread_messages,userid='me'):
        while(len(unread_messages)>0):
            unread_messages_slice = unread_messages[:self.batch_size]
            self.__mark_batch_read(unread_messages_slice, userid)
            unread_messages = unread_messages[self.batch_size:]
        
    
    def __mark_individual_read(self,unread_messages,userid):
        for unread in unread_messages:
            msg_labels = {'removeLabelIds': ['UNREAD'] }
            try:
                message = self.service.users().messages().modify(userId=userid, id=unread['id'],
                                                        body=msg_labels).execute()
                label_ids = message['labelIds']
                print ('Message ID: %s - With Label IDs %s' % (unread['id'], label_ids))
            except errors.HttpError, error:
                print ('An error occurred: %s' % error) 
    

    def __mark_batch_read(self,unread_messages,userid):
        message_ids=[message_ids['id'] for message_ids in unread_messages if 'id' in message_ids]
        msg_labels = {'ids': message_ids , 'removeLabelIds': ['UNREAD'] }
        try:
            message = self.service.users().messages().batchModify(userId=userid,
                                            body=msg_labels).execute()

            print ("Marked %s messages as Read" %len(message_ids))
        except errors.HttpError, error:
            print ('An error occurred: %s' % error)

def lambda_handler(event, context):
    credentials = os.environ["KMS_KEY"]
    #print (credentials)
    gmail_client = Gmail(credentials)
    gmail_client.mark_read(gmail_client.list_unread())
    return ''

if __name__ == '__main__':
    sys.exit(lambda_handler({},{}))