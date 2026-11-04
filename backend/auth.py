import os
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models import User

password_hasher = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)
def secret():
    value = os.getenv('JWT_SECRET', '')
    if len(value) < 32:
        raise RuntimeError('Set JWT_SECRET to at least 32 random characters in .env')
    return value
def token_for(user):
    return jwt.encode({'sub':str(user.id), 'exp':datetime.now(timezone.utc)+timedelta(hours=8)}, secret(), algorithm='HS256')
def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    try:
        if not credentials:
            raise ValueError()
        payload = jwt.decode(credentials.credentials, secret(), algorithms=['HS256'])
        user = db.get(User, int(payload['sub']))
        if not user:
            raise ValueError()
        return user
    except (jwt.PyJWTError, ValueError, KeyError):
        raise HTTPException(401, 'Please sign in to continue.')
def admin(user: User = Depends(current_user)):
    if user.role != 'admin':
        raise HTTPException(403, 'Administrator access required.')
    return user
def user_dict(user):
    return {'id':user.id,'name':user.name,'email':user.email,'role':user.role}
