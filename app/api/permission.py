"""permission module"""
from fastapi import Depends, Request, status
from fastapi_contrib.auth.permissions import BasePermission
from fastapi_contrib.permissions import PermissionsDependency


def set_permissions(*args):
    """
    set permission
    ```
        @router.get(
            '/profile/',
            name='Self User profile',
            response_model=schemas.UserProfile,
            dependencies=set_permissions(
                JWTRequiredPermission
            )
        )
    ```
    """
    permissions = []
    for el in args:
        permissions.append(el)
    return [Depends(PermissionsDependency(permissions))]


class JWTRequiredPermission(BasePermission):
    """auth permission class"""
    error_msg = 'Auth error'
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = status.HTTP_401_UNAUTHORIZED

    def has_required_permisions(self, request: Request) -> bool:
        """check permission"""
        return request.user is not None


class SuperAdminPermission(BasePermission):
    """auth permission class"""
    error_msg = 'Not super admin'
    status_code = status.HTTP_403_FORBIDDEN
    error_code = status.HTTP_403_FORBIDDEN

    def has_required_permisions(self, request: Request) -> bool:
        """check permission"""
        user = request.user
        return user and user.is_super_admin


class HighestPermission(BasePermission):
    """最高權限"""

    def has_required_permisions(self, request: Request) -> bool:
        """權限判斷"""
        if not request.user:
            return True
        return request.user.is_super_admin
