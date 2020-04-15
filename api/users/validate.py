import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _, ngettext


class MaximumLengthValidator:
    """
    Validate whether the password is of less than maximum length.
    """
    def __init__(self, max_length=1024):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(
                ngettext(
                    "This password is too long. It must contain at most %(max_length)d character.",
                    "This password is too long. It must contain at most %(max_length)d characters.",
                    self.max_length
                ),
                code='password_too_long',
                params={'max_length': self.max_length},
            )

    def get_help_text(self):
        return ngettext(
            "Your password must contain at most %(max_length)d character.",
            "Your password must contain at most %(max_length)d characters.",
            self.max_length
        ) % {'max_length': self.max_length}


#
# https://www.owasp.org/index.php/Authentication_Cheat_Sheet
#
class PasswordComplexityValidator:
    """
    Password must meet at least 3 out of the following 4 complexity rules
        at least 1 uppercase character (A-Z)
        at least 1 lowercase character (a-z)
        at least 1 digit (0-9)
        at least 1 special character (punctuation) — do not forget to treat space as special characters too
    """
    def __init__(self, min_upper_case_letters=1,
                       min_lower_case_letters=1,
                       min_digits=1,
                       min_special_characters=1):
        self.min_upper_case_letters = min_upper_case_letters
        self.min_lower_case_letters = min_lower_case_letters
        self.min_digits             = min_digits
        self.min_special_characters = min_special_characters

    def validate(self, password, user=None):

        # at least 1 uppercase character (A-Z)
        if len(re.findall(r'[A-Z]', password)) < self.min_upper_case_letters:
            raise ValidationError(
                ngettext(
                    "Password minimal complexity not met. It must contain at least %(min_upper_case_letters)d upper-case character.",
                    "Password minimal complexity not met. It must contain at least %(min_upper_case_letters)d upper-case characters.",
                    self.min_upper_case_letters
                ),
                code='password_too_short_of_uppercase_letters',
                params={'min_upper_case_letters': self.min_upper_case_letters},
            )

        # at least 1 lowercase character (a-z)
        if len(re.findall(r'[a-z]', password)) < self.min_lower_case_letters:
            raise ValidationError(
                ngettext(
                    "Password minimal complexity not met. It must contain at least %(min_lower_case_letters)d lower-case character.",
                    "Password minimal complexity not met. It must contain at least %(min_upper_case_letters)d lower-case characters.",
                    self.min_lower_case_letters
                ),
                code='password_too_short_of_lowercase_letters',
                params={'min_lower_case_letters': self.min_lower_case_letters},
            )

        # at least 1 digit character (0-9)
        if len(re.findall(r'[0-9]', password)) < self.min_digits:
            raise ValidationError(
                ngettext(
                    "Password minimal complexity not met. It must contain at least %(min_digits)d digit.",
                    "Password minimal complexity not met. It must contain at least %(min_digits)d digits.",
                    self.min_digits
                ),
                code='password_too_short_of_digits',
                params={'min_digits': self.min_digits},
            )

        # at least 1 special character (punctuation) — do not forget to treat space as special characters too
        if len(re.findall(r'''[ !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]+''', password)) < self.min_special_characters:
            raise ValidationError(
                ngettext(
                    "Password minimal complexity not met. It must contain at least %(min_special_characters)d special character.",
                    "Password minimal complexity not met. It must contain at least %(min_special_characters)d special characters.",
                    self.min_special_characters
                ),
                code='password_too_short_of_special_character',
                params={'min_special_characters': self.min_special_characters},
            )

    def get_help_text(self):
        txt = ["Password must contain at least %d upper-case character." %self.min_upper_case_letters,
               "Password must contain at least %d lower-case character." % self.min_lower_case_letters,
               "Password must contain at least %d digits." % self.min_digits,
               "Password must contain at least %d special character." % self.min_special_characters]
        return _("\n".join(txt))