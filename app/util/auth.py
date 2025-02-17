from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import EmailStr
from jose import JWTError, jwt
from app.database.user_crud import get_user_by_email

SECRET_KEY = "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b50e896e11662"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

"""
=> OAuth2PasswordBearer: This class, imported from fastapi.security, is designed specifically for handling OAuth2 Bearer token authentication. It's the core component that allows FastAPI to understand how to expect and verify access tokens.

=> tokenUrl="token": This is the most important part. tokenUrl specifies the URL of your application's token endpoint. The token endpoint is responsible for handling user login (typically username/password) and issuing access tokens (and often refresh tokens as well).

=> In this example, tokenUrl="token" means that your token endpoint is located at the /token path. So, a client (like a web browser or another service) would make a POST request to /token with the user's credentials to get an access token. This is usually done using the OAuth2PasswordRequestForm as the request body.
oauth2_scheme: The result of OAuth2PasswordBearer(tokenUrl="token") is an instance of a security scheme (specifically, a Bearer token scheme). This oauth2_scheme object is what you'll use later with the Depends dependency to protect your API routes.

How it works in the broader authentication flow:

=> Obtaining a Token (Client-Side):  The client first needs to obtain an access token.  It does this by making a request to your /token endpoint (the one you specified in tokenUrl).  The request typically includes the user's username and password.

=> /token Endpoint (Server-Side): Your /token endpoint (which you'll need to implement) handles the login logic. It verifies the user's credentials and, if they're correct, generates an access token (usually a JWT).  It then returns the access token to the client.

=> Accessing Protected Resources (Client-Side): When the client wants to access a protected resource (an API endpoint that requires authentication), it includes the access token in the Authorization header of the HTTP request. The format is very specific and must be: Authorization: Bearer <access_token> which is automatically done by fastapi
"""

def get_hashed_password(plain_password: str):
    # Hash a password
    hashed_password = pwd_context.hash(plain_password)
    return hashed_password

def verify_password(plain_password: str, hashed_password: str):
    # Verify a password
    is_verified = pwd_context.verify(plain_password, hashed_password)
    return is_verified

def authenticate_user(email: EmailStr, password: str):
    try:
        #fetch user details based on email from database
        user = get_user_by_email(email)
    except Exception as e:
        raise e

    #check if user exists
    if not user:
        return False

    #compare the hashed password stored in db with the password after hashing.
    hashed_password = user.password
    if not verify_password(password, hashed_password):
        return False

    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# explaination: oauth2_scheme
"""
When you use Depends(oauth2_scheme) in a protected route:
This tells FastAPI several things:

=> Authentication Required: This route requires authentication. If a user tries to access this route without a valid access token, they will get a 401 Unauthorized error.

=> Bearer Token Expected: FastAPI should expect the access token to be provided in the Authorization header of the HTTP request, using the Bearer scheme.
When a client wants to access a protected resource (an API endpoint), it's the client's responsibility to include a valid access token in the Authorization header of the HTTP request.
Authorization: Bearer <access_token>

=> Token Extraction and Verification: FastAPI will use the oauth2_scheme (the OAuth2PasswordBearer instance) to:
Look for the Authorization header in the incoming request.
Check if the header's value starts with Bearer.
If it does, extract the token (the part after Bearer).
Verify the token. This usually involves checking the token's signature (if you are using JWTs) and making sure it hasn't expired.

=> The extracted and (implicitly) verified token is then assigned to the token parameter.

"""
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userEmail = payload.get("sub")
        if userEmail is None:
            raise credential_exception
        
        user = get_user_by_email(userEmail)
        if user is None:
            raise credential_exception

        return user
    except JWTError:
        raise credential_exception
    except Exception as e:
        raise e
