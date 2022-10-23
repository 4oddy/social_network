from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super(CustomJWTAuthentication, self).get_user(validated_token)
        user.save(update_fields=['last_online'])
        return user
