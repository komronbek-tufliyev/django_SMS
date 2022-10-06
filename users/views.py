import logging

from uuid import uuid4

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.contrib.auth import logout

from users import login
from users.models import User
from users.utils import generate_code
from users.utils import cryptography_fernet_encoder
from users.sms import sms
from users import redis

# Create your views here.

logger = logging.getLogger(__name__)


def homeView(request) -> dict:
    """This method is about home page"""
    if not request.user.is_authenticated:
        return redirect('my-account')

    return render(request, 'users/home.html')


def loginView(request) -> dict:
    """ This method is about login/logout"""
    if request.user.is_authenticated and request.user.is_verified:
        return redirect('home')

    page: str = 'my-account'
    code: str = generate_code()
    user: User = None 

    if request.method == 'POST':
        phone = request.POST.get('phone').replace('+', '')
        print(phone)

        try:
            with transaction.atomic():
                user = User.objects.get(phone=phone, is_deleted=False)
                if user is not None:
                    user.is_verified = False
                    sms._send_verify_code(user.phone, code)
                    user.save()
                    context: dict = {
                        'request': request,
                        'user': user,
                        'code': code,
                    } 

                    login(**context)

                    return redirect('confirm')

        except User.DoesNotExist:
            page: str = 'register'

    context: dict = {
        'page': page,
    }

    return render(request, 'users/login.html', context)


def registerView(request) -> dict:
    if request.user.is_authenticated and request.user.is_verified:
        return redirect('home')

    if request.method == 'POST':
        context: dict = {}
        password, key = cryptography_fernet_encoder(str(uuid4()).replace('-', '')[:12])

        try:
            context['key'] = key
            context['password'] = password.decode()
            context['full_name'] = request.POST.get('name')
            context['phone'] = request.POST.get('phone').replace('+', '')

            code: str = generate_code()
            print(code)
               
            try:
                user: User = User.objects.get(phone=context['phone'])

                if user.is_authenticated and user.is_verified:
                    print("User is authenticated and verified")
                    return redirect('home')

                sms._send_verify_code(user.phone, code)
                context: dict = {
                    'user': user,
                    'code': code,
                    'request': request,
                }

                if user.is_authenticated and not user.is_verified:
                    login(**context)
                    print("Authenticated user is not verified")
                    return redirect('confirm')

            except User.DoesNotExist:
                logger.info("User does not exist")

            user = User.objects.create(**context)

            with transaction.atomic():
                if user is not None:
                    user.is_verified = False
                    sms._send_verify_code(user.phone, code)
                    user.save()

                    context: dict = {
                        'request': request,
                        'user': user,
                        'code': code,
                    }
                    login(**context)

                return redirect('confirm')

        except Exception as e:
            logger.error(e)
            messages.error(request, 'Something went wrong')

    return render(request, 'users/login.html')


def verifyView(request) -> None:
    """This method verifies user if they have verified code"""
    page: str = 'confirm'
    code: str = request.POST.get('code')
    print("Code: ", code)
    session_id: str = request.COOKIES.get('sessionid')
    print(f"Sessioon id: {session_id}")
    checked: bool = redis._check_code_in_redis(session_id, code)
    print(f"Checked: {checked}")
    try:
        if checked:
            user: User = User.objects.get(id=request.user.id, is_deleted=False)
            if user:
                user.is_verified = True
                user.is_authenticated = True
                user.save()
                print("User is verified", 'redirecting to home')
                return redirect('home')
    except:
        logger.error('User not found')
        messages.error(request, 'User not found')
        pass

    if request.user.is_authenticated and request.user.is_verified:
        return redirect('home')

    if request.method == 'POST' and request.user.is_authenticated:
        try:
            user: User = User.objects.get(
                id=int(request.user.id), 
                phone=str(request.user.phone),
                is_deleted=False,
                eskiz_code=str(code),
            )
            user.is_verified = True
            user.save()

            if user is not None and user.is_verified:
                messages.success(request, f"Xush kelibsiz {user.full_name}")
                login(request, user)
                return redirect('home')

        except User.DoesNotExist:
            error: str = "Tasdiqlash kodini noto'g'ri kiritdingiz"
            logger.error(f"Error during user verification: {error}")
            messages.error(request, 'User not found in database')
            return redirect('my-account')

    

    return render(request, 'users/login.html', {'page': page})


def logoutView(request) -> None:
    """Remove the authenticated user's ID from the request and flush their session data"""
    logout(request)
    return redirect('home') 


def show_user_info(request):
    users = User.objects.all().order_by('-id')
    context = {
        'users': users,
    }

    return render(request, 'users/user_info.html', context)
