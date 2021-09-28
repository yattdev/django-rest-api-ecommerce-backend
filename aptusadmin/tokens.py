from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six

from myapps.models import CustomUser


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        customuser = CustomUser.objects.get(user_ptr=user.id)
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(customuser.email_is_valid)
        )


class PasswordResetTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp)
        )


account_activation_token = TokenGenerator()
password_reset_token = PasswordResetTokenGenerator()
