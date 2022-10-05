import logging

from requests import request
from requests.structures import CaseInsensitiveDict

from django.conf import settings
from users.models import SMSClient as sms_model

logger = logging.getLogger(__name__)


class SMSClient:
    __GET = 'get'
    __POST = 'post'
    __PATCH = 'patch'
    __DELETE = 'delete'
    __CONTACT = 'contact'

    STATUS_SUCCESS = 'success'

    __AUTH_USER = 'auth/user'
    __AUTH_LOGIN = 'auth/login'
    __AUTH_REFRESH = 'auth/refresh'
    __AUTH_INVALIDATE = 'auth/invalidate'
    __AUTH_SEND_VERIFY_CODE = 'message/sms/send'
    __AUTH_TOKEN_ERROR = " Error creating sms client token\n"
    __AUTH_VERIFY_CODE_TEXT = "Sizning tasdiqlash kodingiz: "

    __ERROR_WITH_ESKIZ_PROCESSING = "⚠️ Failed to request\n\n <code>url: {}\n\ndata: {}\n\nresponse: {}</code>"

    def __init__(self, base_url: str, email: str, password: str, group: str, callback_url: str) -> None:
        self.email = email
        self.group = group
        self.password = password
        self.base_url = base_url
        self.callback_url = callback_url

        self.headers: CaseInsensitiveDict = CaseInsensitiveDict()

    def __request(self, api_path: str, data: dict=None, **kwargs) -> dict:
        """ Custom request method"""
        context: dict = {
            'data': data,
            'method': kwargs.pop('method', None),
            'headers': kwargs.pop('headers', None),
            'url': self.base_url + api_path,
        }

        try: 
            return request(**context).json()
        except Exception as e:
            err: str = self.__ERROR_WITH_ESKIZ_PROCESSING.format(
                context['url'], context['data'], e
            )
            logger.error(err)

    def _auth(self) -> dict:
        data: dict = {
            'email': self.email,
            'password': self.password,
        }

        context: dict = {
            'data': data,
            'method': self.__POST,
            'api_path': self.__AUTH_LOGIN,
        }
        token: str = self.__request(**context).get('data')['token']
        sms_model.objects.get_or_create(token=token)

        return self.__request(**context)

    def _refresh_token(self) -> dict:
        self.headers['Authorization'] = 'Bearer ' + self.get_sms_client_token()
        context: dict = {
            'headers': self.headers,
            'method': self.__PATCH,
            'api_path': self.__AUTH_REFRESH,
        }
        
        return self.__request(**context)

    def __invalidate_token(self) -> dict:
        self.headers['Authorization'] = 'Bearer ' + self.get_sms_client_token()
        context: dict = {
            'headers': self.headers,
            'method': self.__DELETE,
            'api_path': self.__AUTH_INVALIDATE,
        }

        return self.__request(**context)

    
    def _get_my_user_info(self) -> dict:
        self.headers['Authorization'] = 'Bearer ' + self.get_sms_client_token()

        context: dict = {
            'method': self.__GET,
            'headers': self.headers,
            'api_path': self.__AUTH_USER,
        }

        return self.__request(**context)

    def _add_sms_contact(self, **kwargs) -> dict:
        self.headers['Authorization'] = 'Bearer ' + self.get_sms_client_token()

        data: dict = {
            'name': kwargs.get('full_name'),
            'email': kwargs.get('email'),
            'group': kwargs.get('group'),
            'mobile': kwargs.get('phone'),
        }

        context: dict = {
            'data': data,
            'method': self.__POST,
            'headers': self.headers,
            'api_path': self.__CONTACT,
        }

        return self.__request(**context)

    
    def _send_verify_code(self, phone: str, code: str) -> dict:
        self.headers['Authorization'] = 'Bearer ' + self.get_sms_client_token()

        data: dict = {
            'from': 4546,
            'mobile_phone': phone,
            'callback_url': self.callback_url,
            'message': self.__AUTH_VERIFY_CODE_TEXT + code,
        }

        context: dict = {
            'data': data,
            'method': self.__POST,
            'headers': self.headers,
            'api_path': self.__AUTH_SEND_VERIFY_CODE,
        }

        resp = self.__request(**context)

        return resp

    
    def get_sms_client_token(self) -> str:
        try:
            token: str = sms_model.objects.only('token').last().token

        except Exception as e:
            self._auth()

        return token

sms = SMSClient(
    **settings.SMS_SERVICE
)
