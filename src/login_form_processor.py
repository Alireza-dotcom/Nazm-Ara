from email_validator import validate_email, EmailNotValidError
import re


class LoginFormProcessor:
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


    def validateFields(self, field_map):
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
