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


    def validateSignupFields(self, field_map):
        errors = []
        invalid_widgets = []

        # Content validations
        if "email" in field_map:
            normalized_email = self.validateEmailField(field_map["email"])
        if normalized_email is False:
            errors.append("email format is invalid")
            invalid_widgets.append(field_map["email"])

        if "password" in field_map and not self.checkLength(field_map["password"], min_len=8, max_len=50):
            errors.append("password must be at least 8 characters")
            invalid_widgets.append(field_map["password"])
        elif "password" in field_map and not self.validatePassword(field_map["password"])[0]:
            _, pwd_reason = self.validatePassword(field_map["password"])
            errors.append(pwd_reason)
            invalid_widgets.append(field_map["password"])

        if "first_name" in field_map and not self.checkLength(field_map["first_name"], min_len=3, max_len=30):
            errors.append("first name must be at least 3 characters")
            invalid_widgets.append(field_map["first_name"])
        elif "first_name" in field_map and not self.validateName(field_map["first_name"]):
            errors.append("first name format is invalid")
            invalid_widgets.append(field_map["first_name"])

        if "last_name" in field_map and not self.checkLength(field_map["last_name"], min_len=3, max_len=30):
            errors.append("last name must be at least 3 characters")
            invalid_widgets.append(field_map["last_name"])
        elif "last_name" in field_map and not self.validateName(field_map["last_name"]):
            errors.append("last name format is invalid")
            invalid_widgets.append(field_map["last_name"])

        if "nickname" in field_map and not self.checkLength(field_map["nickname"], min_len=3, max_len=25):
            errors.append("nickname must be at least 2 characters")
            invalid_widgets.append(field_map["nickname"])
        elif "nickname" in field_map and not self.validateNickname(field_map["nickname"]):
            errors.append("nickname format is invalid")
            invalid_widgets.append(field_map["nickname"])

        if errors:
            return False, {
                "errors": errors,
                "invalid_widgets": invalid_widgets
            }

        # Build validated fields dict
        validated = {}
        for name, widget in field_map.items():
            if name == "email":
                validated[name] = self.validateEmailField(widget)
            elif name == "first_name":
                validated[name] = self.validateName(widget)
            elif name == "last_name":
                validated[name] = self.validateName(widget)
            elif name == "nickname":
                validated[name] = self.validateName(widget)
            elif name == "password":
                validated[name] = self.getFieldText(widget)
            else:
                print("Unknown field:", name)
                return False, {
                    "errors": [f"Unknown field: {name}"],
                    "invalid_widgets": [widget]
                }

        return True, validated


    def validateLoginFields(self, field_map):
        errors = []
        invalid_widgets = []

        # Content validations
        if "email" in field_map:
            normalized_email = self.validateEmailField(field_map["email"])
        if normalized_email is False:
            errors.append("email format is invalid")
            invalid_widgets.append(field_map["email"])

        if "password" in field_map and not self.checkLength(field_map["password"], min_len=8, max_len=50):
            errors.append("password must be at least 8 characters")
            invalid_widgets.append(field_map["password"])

        if errors:
            return False, {
                "errors": errors,
                "invalid_widgets": invalid_widgets
            }

        # Build validated fields dict
        validated = {}
        for name, widget in field_map.items():
            if name == "email":
                validated[name] = self.validateEmailField(widget)
            elif name == "password":
                validated[name] = self.getFieldText(widget)
            else:
                print("Unknown field:", name)
                return False, {
                    "errors": [f"Unknown field: {name}"],
                    "invalid_widgets": [widget]
                }

        return True, validated


    def validateForgotPassFields(self, field_map):
        errors = []
        invalid_widgets = []

        # Content validations
        if "email" in field_map:
            normalized_email = self.validateEmailField(field_map["email"])
        if normalized_email is False:
            errors.append("email format is invalid")
            invalid_widgets.append(field_map["email"])

        if errors:
            return False, {
                "errors": errors,
                "invalid_widgets": invalid_widgets
            }

        # Build validated fields dict
        validated = {}
        for name, widget in field_map.items():
            if name == "email":
                validated[name] = self.validateEmailField(widget)
            else:
                print("Unknown field:", name)
                return False, {
                    "errors": [f"Unknown field: {name}"],
                    "invalid_widgets": [widget]
                }

        return True, validated
