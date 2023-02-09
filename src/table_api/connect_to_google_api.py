import apiclient
import httplib2
from oauth2client.service_account import ServiceAccountCredentials

from config.secret_config import GOOGLE_API_CREDENTIALS_FILE


def connect_to_google_api():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_API_CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])

    http_auth = credentials.authorize(httplib2.Http())
    return apiclient.discovery.build('sheets', 'v4', http=http_auth)
