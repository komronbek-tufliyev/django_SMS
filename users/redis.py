from redis import StrictRedis
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Redis:
    __EXPIRE_TIME = 100
    
    def __init__(self) -> None:
        self.__redis = StrictRedis(**(settings.REDIS))

    def _set_verify_code(self, session_id: str, phone: str, verify_code: str='') -> str:
        """This method helps to set verification code for given phone number in redis"""
        try:
            cache_date: dict = {
            'name': session_id,
            'time': self.__EXPIRE_TIME,
            'value': phone,
            }
            print(f"Cache_data: {cache_date}")
            self.__redis.setex(**cache_date)
        except Exception as e:
            print(f"Error on set_verify_code: {e}")
            logger.error(e)
            return False
        
    def _is_already_sent(self, phone: str) -> bool:
        """ This method checks if the sms verify code already sent or not"""
        try:    
            return bool(self.__redis.exists(phone))
        except Exception as e:
            print(f"Error on is_already_sent method: {e}")
            logger.error(e)
            return False

    def _check_code_in_redis(self, session_id: str, code: str) -> bool:
        code_in_redis: str = self.__redis.get(session_id)
        print(f"Code in redis: {str(code_in_redis.decode('utf-8'))}")
        try:
            if code_in_redis:
                return str(code_in_redis.decode('utf-8')) == code
        except Exception as e:
            print(f"Error on check_code_in_redis: {e}")
            logger.error(e)
            pass
        return False

redis = Redis()