import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from ..mdl import User
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from ..database import SessionLocal, get_db, Base
from sqlalchemy.orm import Session
from uuid import UUID


# Secret key used to encode/decode the JWT
SECRET_KEY = "hR4gtd_40OLbIgt0dK1sfnm6ZfTVWG-5r_a-K_Z19nw"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token. If `expires_delta` is provided, the token will expire after that duration.
    Otherwise, the token will not expire (unlimited lifetime).
    """
    to_encode = data.copy()
    
    # Convert UUID to string for JWT encoding
    if 'sub' in to_encode and isinstance(to_encode['sub'], UUID):
        to_encode['sub'] = str(to_encode['sub'])
    
    # Only include expiration if `expires_delta` is provided
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    try:
        # Extract token from Authorization header
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        token = authorization[7:]  # Remove 'Bearer ' prefix
        
        # Decode the token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        
        # Extract user ID from token
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing user ID")
        
        # Query the user directly from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=401, detail="Could not validate credentials")
