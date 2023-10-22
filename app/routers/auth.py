import pyotp
import requests
from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi import status

from app.models.auth import UserCreateSchema, User
from app.utils.auth import check_password, hash_password, verify_password, create_jwt_token
from app.database import get_db
from settings import templates, SECRET_KEY_CLOUDFLARE

router = APIRouter()

# Connect to Redis (using db0 for attempts and db1 for blocked users for time)


@router.get('/login', response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post('/login', response_class=HTMLResponse)
async def login_page(request: Request, user: UserCreateSchema = Depends(UserCreateSchema.as_form), db: Session = Depends(get_db)):
    res = db.query(User).filter_by(email=user.email).first()
    if not res:
        return RedirectResponse("/auth/register?err_msg=No user with such email",
                                status_code=status.HTTP_302_FOUND,
                                headers={'err': 'No user with such email'})

    try:
        if not verify_password(user.password, res.password):
            raise ValueError
    except ValueError:
        return RedirectResponse("/auth/register?err_msg=Password not passed",
                                status_code=status.HTTP_302_FOUND,
                                headers={'err': 'Password not passed'})

    res = pyotp.parse_uri(res.otp_secret).verify(user.otp_verif_code)
    if not res:
        return RedirectResponse("/auth/register?err_msg=OTP code not correct", status_code=status.HTTP_302_FOUND)

    template = templates.TemplateResponse("main.html", context={'request': request, 'email': user.email})
    jwt = create_jwt_token({
        'email': user.email,
        'password': user.password
    })
    template.set_cookie('token', jwt)
    return template


@router.get('/register')
async def login_page(request: Request, err_msg: str = None):
    otp_secret = pyotp.totp.TOTP(pyotp.random_base32()).provisioning_uri(name='replace_it', issuer_name='Lab4')
    return templates.TemplateResponse("register.html", context={'request': request, 'err_msg': err_msg, 'otp_secret': otp_secret})


@router.post('/register')
async def login_page(request: Request, user: UserCreateSchema = Depends(UserCreateSchema.as_form), cf_turnstile=Form(alias='cf-turnstile-response'), db: Session = Depends(get_db)):
    captcha_res = requests.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', data={'secret': SECRET_KEY_CLOUDFLARE,
                                                                                     'response': cf_turnstile,
                                                                                     'remoteip': request.headers.get('CF-Connecting-IP')}).json()
    if not captcha_res.get('success'):
        return RedirectResponse("/auth/register?err_msg=Captcha not solved", status_code=status.HTTP_302_FOUND)

    res = pyotp.parse_uri(user.otp_secret.replace('amp;', '')).verify(user.otp_verif_code)
    if not res:
        return RedirectResponse("/auth/register?err_msg=OTP code not correct", status_code=status.HTTP_302_FOUND)
    if not check_password(user.password):
        return RedirectResponse("/auth/register?err_msg=Password not passed", status_code=status.HTTP_302_FOUND)

    user.password = hash_password(user.password)
    user_dump = user.model_dump()
    del user_dump['otp_verif_code']
    db_parent = User(**user_dump)
    db.add(db_parent)
    db.commit()
    db.refresh(db_parent)
    template = templates.TemplateResponse("main.html", context={'request': request, 'email': user.email})
    jwt = create_jwt_token({
        'email': user.email,
        'password': user.password
    })
    template.set_cookie('token', jwt)
    return template
