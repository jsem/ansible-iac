#!/usr/bin/python3

from __future__ import print_function
import pickle
import os
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def main():
    """Exports and saves database backups.
    Prints the names and ids of the first 10 files the user has access to.
    """
    dumpPostgres()
    encryptDump()
    credentials = loadCredentials()
    service = createService(credentials)
    uploadEncryptedDump(service)
    removeDump()

def dumpPostgres():
    subprocess.run("su -c '/usr/bin/pg_dump --column-inserts --data-only -f /tmp/jsemple-dev-backup.sql jsemple-dev' postgres",shell=True)

def encryptDump():
    subprocess.run("gpg --output /tmp/jsemple-dev-backup.sql.gpg --encrypt --recipient james.robert.semple@gmail.com /tmp/jsemple-dev-backup.sql",shell=True)

def removeDump():
    os.remove('/tmp/jsemple-dev-backup.sql')
    os.remove('/tmp/jsemple-dev-backup.sql.gpg')

def loadCredentials():
    credentials = None

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        # Refresh the access token if required
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    return credentials

def createService(creds):
    return build('drive', 'v3', credentials=creds)

def uploadEncryptedDump(service):
    # Call the Drive v3 API
    file_metadata = {'name': 'jsemple-dev-backup.sql.gpg'}
    media = MediaFileUpload('/tmp/jsemple-dev-backup.sql.gpg', mimetype='text/plain')
    return service.files().create(body=file_metadata, media_body=media).execute()

if __name__ == '__main__':
    main()
