import string

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

from allauth.account.adapter import DefaultAccountAdapter


User = get_user_model()


class AccountAdapter(DefaultAccountAdapter):
    """A custom account adapter where we modify behaviour for our use case."""

    def set_phone(self, user: User, phone: str, verified: bool) -> None:
        user.phone = phone
        user.phone_verified = verified
        user.save(update_fields=["phone", "phone_verified"])

    def get_phone(self, user: User) -> tuple[str, bool] | None:
        if user.phone:
            return user.phone, user.phone_verified
        return None

    def get_user_by_phone(self, phone: str) -> User | None:
        return (
            User.objects.filter(phone=phone)
            .order_by("-phone_verified")
            .first()
        )

    def generate_phone_verification_code(
        self, *, user: User, phone: str
    ) -> str:
        """Overwrite allauth method to generate a numeric OTP code."""

        return get_random_string(length=4, allowed_chars=string.digits)

    def set_phone_verified(self, user: User, phone: str) -> None:
        self.set_phone(user, phone, True)

    def send_verification_code_sms(
        self, user: User, phone: str, code: str, **kwargs
    ) -> None:
        messages.warning(
            self.request,
            f"⚠️ SMS demo stub: assume code {code} was sent to {phone}.",
        )

    def send_unknown_account_sms(self, phone: str, **kwargs) -> None:
        messages.warning(
            self.request,
            f"⚠️ SMS demo stub: Enumeration prevention: texted {phone} informing no account exists.",
        )

    def send_account_already_exists_sms(self, phone: str, **kwargs) -> None:
        messages.warning(
            self.request,
            f"⚠️ SMS demo stub: Enumeration prevention: texted {phone} informing account already exists.",
        )
