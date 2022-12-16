from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWTAuthentication(JWTAuthentication):
    """ Custom JWT Authentication class
        It is used to set user online
    """
    def get_user(self, validated_token):
        user = super(CustomJWTAuthentication, self).get_user(validated_token)
        # setting last online
        user.save(update_fields=['last_online'])
        return user
