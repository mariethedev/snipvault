from rest_framework import status
from rest_framework.exceptions import APIException




class AuthenticationFailed(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Current password is incorrect.Please try again'
    default_code = 'incorrect_password'

class SamePasswordException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'New password must be different from old password'
    default_code = 'same_password'

class PasswordMismatchError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'New password and confirm password do not match.'
    default_code = 'password_mismatch_error'

class RequiredFieldsError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Both email and password are required.'
    default_code = 'required_fields'
    
class UserDoesNotExistError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'No user with such email exists.'
    default_code = 'user_doesnot_exist'

class IncorrectPasswordError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid credentials, try again'
    default_code = 'wrong_password'


class GoogleAuthenticationFailed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to authenticate user'
    default_code = 'google_authentication_failed'


class AuthorizationCodeError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Authorization code is required'
    default_code = 'authorization_code _not_found'






