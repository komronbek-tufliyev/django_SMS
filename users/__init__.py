from django.contrib.auth import _get_backends
from django.middleware.csrf import rotate_token
from django.contrib.auth import _get_user_session_key
from django.utils.crypto import constant_time_compare

from django.contrib.auth import (
    SESSION_KEY,
    HASH_SESSION_KEY,
    BACKEND_SESSION_KEY,    
)
from django.contrib.auth.signals import user_logged_in
from users.redis import redis


def login(request, user, backend=None, code: str=None) -> None:
    print("This is login method")
    """This method helps to user login with session"""
    session_auth_hash: str = ''
    if user is None:
        user = request.user
    if hasattr(user, 'get_session_auth_hash'):
        session_auth_hash = user.get_session_auth_hash()
        print(f"Session auth hash: {session_auth_hash}")

    if SESSION_KEY in request.session:
        if _get_user_session_key(request) != user.pk or (
            session_auth_hash and not constant_time_compare(request.session.get('HASH_SESSION_KEY', ''), session_auth_hash)):
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
            print("Session flushed")
    else:
        print("Session not flushed")
        request.session.cycle_key()

    
    try:
        backend = backend or user.backend

    except AttributeError:
        backends = _get_backends(return_tuples=True)
        if len(backends) == 1:
            _, backend = backends[0]
        else:
            raise ValueError(
                'You have multiple authentication backends configured and '
                'therefore must provide the `backend` argument or set the '
                '`backend` attribute on the user.'
            )

    else:
        if not isinstance(backend, str):
            raise TypeError(
                'The `backend` argument must be a dotted import path string (got %r).' % backend
            ) 

    request.session[SESSION_KEY] = user._meta.pk.value_to_string(user)
    request.session[BACKEND_SESSION_KEY] = backend
    request.session[HASH_SESSION_KEY] = session_auth_hash
    if not request.session.session_key:
        request.session.create()
        print("Session key created in __init__/login")
    
    session_id = request.session.session_key
    redis._set_verify_code(session_id, code)
    if hasattr(request, 'user'):
        request.user = user
    
    rotate_token(request)
    user_logged_in.send(sender=user.__class__, request=request, user=user)

