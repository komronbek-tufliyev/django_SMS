from redis import StrictRedis
from django.conf import settings

class Redis:
    __EXPIRE_TIME = 100
    
    def __init__(self) -> None:
        self.__redis = StrictRedis(**(settings.REDIS))

    def _set_verify_code(self, session_id: str, phone: str, code: str) -> str:
        """This method helps to set verification code for given phone number in redis"""
        cache_date: dict = {
            'name': session_id,
            'time': self.__EXPIRE_TIME,
            'value': phone,
        }
        self.__redis.setex(**cache_date)
        
    def _is_already_sent(self, phone: str) -> bool:
        """ This method checks if the sms verify code already sent or not"""
        return bool(self.__redis.exists(phone))

    def _check_code_in_redis(self, session_id: str, code: str) -> bool:
        code_in_redis: str = self.__redis.get(session_id)
        if code_in_redis:
            return code_in_redis.decode() == code
        return False

redis = Redis()