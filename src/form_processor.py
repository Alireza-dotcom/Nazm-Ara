from PySide6.QtWidgets import QLineEdit, QWidget 
from PySide6.QtCore import QObject
from email_validator import validate_email, EmailNotValidError
from zxcvbn import zxcvbn


class FormProcessor(QObject):
    """Handles data extraction and validation logic for all forms within the application."""
    def __init__(self,  parent: QWidget):
        super().__init__(parent)


    def authenticationValidator(self, field_map: list):
            data = {}
            for field_details in field_map:
                field_name = field_details.get("field_name")
                if field_name in ["first_name", "last_name", "nickname"]:
                    data[field_name] = self.validateName(field_details)
                elif field_name == "email":
                    data[field_name] = self.validateEmail(field_details)
                elif field_name == "password":
                    data[field_name] = self.validatePassword(field_details)

            if None in data.values():
                return False

            return data


    def taskModalValidator(self, field_map: list):
        data = {}
        for field_details in field_map:
            field_name = field_details.get("field_name")
            if field_name in ["title", "description"]:
                data[field_name] = self.validateModalGenericField(field_details)
            elif field_name == "priority":
                data[field_name] = self.validatePriority(field_details)
        
        if None in data.values():
            return False

        return data


    def habitModalValidator(self, field_map: list):
            data = {}
            for field_details in field_map:
                field_name = field_details.get("field_name")
                if field_name in ["title", "question", "unit", "description"]:
                    data[field_name] = self.validateModalGenericField(field_details)
                elif field_name == "target":
                    data[field_name] = self.validateTarget(field_details)
                elif field_name == "priority":
                    data[field_name] = self.validatePriority(field_details)
                elif field_name == "color":
                    data[field_name] = self.validateColor(field_details)

            if None in data.values():
                return False

            return data


    def dailyHabitModalValidator(self, field_map: list):
            data = {}
            for field_details in field_map:
                field_name = field_details.get("field_name")
                if field_name == "value":
                    data[field_name] = self.validateTarget(field_details)

            if None in data.values():
                return False

            return data


    def validateModalGenericField(self, field_details: dict):
        field_object = field_details.get("field_object")
        is_optional = field_details.get("is_optional")
        field_input = field_details.get("field_input")

        if not is_optional:
            if self.isFieldFilled(field_input):
                text = self.getFieldText(field_input)
                clean_text = " ".join(text.split())

                field_object.updateError(field_input, error_message="")
            else:
                field_object.updateError(field_input, error_message="This can't be empty.")
                return None
        else:
            text = self.getFieldText(field_input)
            clean_text = " ".join(text.split())

        return clean_text


    def isFieldFilled(self, field: QLineEdit):
        return self.getFieldText(field)


    def getFieldText(self, field: QLineEdit):
        return field.text().strip()


    def validatePriority(self, field_details: dict):
        priority_field = field_details.get("field_object")

        priority = priority_field.currentText()
        valid_priorities = ["Low", "Medium", "High"]
        if priority not in valid_priorities:
            return None

        return valid_priorities.index(priority)


    def validateColor(self, field_details: dict):
        field_object = field_details.get("field_object")
        return field_object.getColor()


    def validateTarget(self, field_details: dict):
        field_object = field_details.get("field_object")
        is_optional = field_details.get("is_optional")
        field_input = field_details.get("field_input")

        if not is_optional:
            if self.isFieldFilled(field_input):
                target = int(self.getFieldText(field_input))
                field_object.updateError(field_input, error_message="")
            else:
                field_object.updateError(field_input, error_message="This can't be empty.")
                return None
        else:
            target = int(self.getFieldText(field_input))

        return target


    def validateName(self, field_details: dict):
        field_object = field_details.get("field_object")
        field_input = field_details.get("field_input")
        min_length = field_details.get("min_length")

        if not self.isFieldFilled(field_input):
            field_object.updateError(field_input, error_message="This can't be empty.")
            return None

        if not self.checkLength(min_length=min_length, field=field_input):
            field_object.updateError(field_input, error_message=f"Must be atleast {min_length} character.")
            return None

        text = self.getFieldText(field_input)
        clean_text = " ".join(text.split())

        field_object.updateError(field_input, error_message="")

        return clean_text


    def checkLength(self, min_length: int, field: QLineEdit):
            field_length = len(self.getFieldText(field))
            return min_length <= field_length


    def validateEmail(self, field_details: dict):
        field_input = field_details.get("field_input")
        field_object = field_details.get("field_object")

        if not self.isFieldFilled(field_input):
            field_object.updateError(field_input, error_message="This can't be empty.")
            return None

        email_text = self.getFieldText(field=field_input)
        try:
            emailinfo = validate_email(email_text, check_deliverability=False)
            field_object.updateError(field_input, error_message="")
            return emailinfo.normalized
        except EmailNotValidError:
            field_object.updateError(field_input, error_message="Email format is not valid")
            return None


    def validatePassword(self, field_details: dict):
        field_object = field_details.get("field_object")
        field_input = field_details.get("field_input")
        min_length = field_details.get("min_length")
        quality_check = field_details.get("quality_check")

        if not self.isFieldFilled(field_input):
            field_object.updateError(field_input, error_message="This can't be empty.")
            return None

        if not self.checkLength(min_length=min_length, field=field_input):
            field_object.updateError(field_input, error_message=f"Must be atleast {min_length} character.")
            return None

        password = self.getFieldText(field_input)

        if quality_check:
            results = zxcvbn(password)

            if results.get("score") < 3:
                reason = results.get('feedback').get("warning") or "Password is too guessable."
                field_object.updateError(field_input, error_message=reason)
                return None

        field_object.updateError(field_input, error_message="")
        return password


    def forgotPasswordValidator(self, field_map: list):
            data = {}
            for field_details in field_map:
                field_name = field_details.get("field_name")
                if field_name == "email":
                    data[field_name] = self.validateEmail(field_details)

            if None in data.values():
                return False

            return data
