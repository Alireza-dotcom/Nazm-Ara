from email_validator import validate_email, EmailNotValidError
from zxcvbn import zxcvbn
import re


class FormProcessor:
    def findEmptyAndFilledFields(self, fields: list):
        empty = []
        for field in fields:
            if not self.getFieldText(field):
                empty.append(field)

        filled = [field for field in fields if field not in empty]

        return {
            "empty": empty,
            "filled": filled
        }


    def getFieldText(self, field):
        return field.text().strip() if hasattr(field, "text") else str(field).strip()


    def validateName(self, name_field):
        name = self.getFieldText(name_field)
        clean_name = " ".join(name.split())

        pattern = r"^[a-zA-Z\u0600-\u06FF\s]+$"
        if not re.match(pattern, clean_name):
            return False

        return clean_name


    def validateNickname(self, nickname_field):
        nickname = self.getFieldText(nickname_field)

        pattern = r"^[a-zA-Z\u0600-\u06FF0-9_]+$"
        if not re.match(pattern, nickname):
            return False

        return nickname


    def validatePassword(self, password_field):
        password = self.getFieldText(password_field)
        results = zxcvbn(password)

        if results['score'] < 3:
            reason = results['feedback']['warning'] or "Password is too guessable."
            return False, reason

        return True, "Strong password."


    def validateEmailField(self, email_field):
        email_text = self.getFieldText(email_field)
        try:
            emailinfo = validate_email(email_text, check_deliverability=False)
            return emailinfo.normalized
        except EmailNotValidError:
            return False


    def checkLength(self, field, min_len: int = 0, max_len: int = 255):
        field_length = len(self.getFieldText(field))
        return min_len <= field_length <= max_len


    def getValidationErrors(self, field_map, is_signup=False):
        errors = []
        invalid_widgets = []

        for name, widget in field_map.items():
            # Name Rules (Length > 3)
            if name in ["first_name", "last_name"]:
                if not self.checkLength(widget, min_len=3, max_len=50):
                    errors.append(f"{name.replace('_', ' ')} must be at least 3 characters")
                    invalid_widgets.append(widget)
                elif not self.validateName(widget):
                    errors.append(f"{name.replace('_', ' ')} format is invalid")
                    invalid_widgets.append(widget)

            # Nickname Rules
            if name == "nickname":
                if not self.checkLength(widget, min_len=2, max_len=255):
                    errors.append("nickname must be at least 3 characters")
                    invalid_widgets.append(field_map["nickname"])
                elif not self.validateNickname(widget):
                    errors.append("nickname format is invalid")
                    invalid_widgets.append(widget)

            # Email Rules
            elif name == "email":
                if self.validateEmailField(widget) is False:
                    errors.append("email format is invalid")
                    invalid_widgets.append(widget)

            # Password Rules
            elif name == "password":
                # Rule: Always check length > 8
                if not self.checkLength(widget, min_len=8, max_len=50):
                    errors.append("password must be at least 8 characters")
                    invalid_widgets.append(widget)
                elif is_signup:
                    valid, reason = self.validatePassword(widget)
                    if not valid:
                        errors.append(reason)
                        invalid_widgets.append(widget)

        if errors:
            return False, {"errors": errors, "invalid_widgets": invalid_widgets}
        return True, None


    def getValidatedData(self, field_map):
        validated = {}
        for name, widget in field_map.items():
            if name == "email":
                validated[name] = self.validateEmailField(widget)
            elif name in ["first_name", "last_name"]:
                validated[name] = self.validateName(widget)
            elif name == "nickname":
                validated[name] = self.validateNickname(widget)
            elif name == "password":
                validated[name] = self.getFieldText(widget)
            else:
                validated[name] = self.getFieldText(widget)
        return validated
