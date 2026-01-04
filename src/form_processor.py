from email_validator import validate_email, EmailNotValidError
from zxcvbn import zxcvbn
import re

from PySide6.QtWidgets import QWidget


class FormProcessor:
    """Handles data extraction and validation logic for all forms within the application."""

    def findEmptyAndFilledFields(self, fields: list):
        """Categorizes widgets into empty and filled lists for UI feedback."""
        empty = []
        for field in fields:
            if not self.getFieldText(field):
                empty.append(field)

        filled = [field for field in fields if field not in empty]

        return {
            "empty": empty,
            "filled": filled
        }


    def getFieldText(self, field: QWidget):
        return field.text().strip() if hasattr(field, "text") else str(field).strip()


    def validateName(self, name_field: QWidget):
        """Validates first/last names allowing Latin and Persian characters."""
        name = self.getFieldText(name_field)
        # Normalize whitespace
        clean_name = " ".join(name.split())

        # Regex for English and Arabic/Persian scripts
        pattern = r"^[a-zA-Z\u0600-\u06FF\s]+$"
        if not re.match(pattern, clean_name):
            return False

        return clean_name


    def validateNickname(self, nickname_field: QWidget):
        """Validates nicknames allowing alphanumeric characters, Persian, and underscores."""
        nickname = self.getFieldText(nickname_field)

        pattern = r"^[a-zA-Z\u0600-\u06FF0-9_]+$"
        if not re.match(pattern, nickname):
            return False

        return nickname


    def validatePassword(self, password_field: QWidget):
        """Assesses password strength using the zxcvbn library."""
        password = self.getFieldText(password_field)
        results = zxcvbn(password)

        if results.get("score") < 3:
            reason = results.get('feedback').get("warning") or "Password is too guessable."
            return False, reason

        return True, "Strong password."


    def validateEmailField(self, email_field):
        """Validates email syntax and returns the normalized email string."""
        email_text = self.getFieldText(email_field)
        try:
            emailinfo = validate_email(email_text, check_deliverability=False)
            return emailinfo.normalized
        except EmailNotValidError:
            return False


    def checkLength(self, field, min_len: int = 0, max_len: int = 255):
        """Checks if the field text length is within the specified bounds."""
        field_length = len(self.getFieldText(field))
        return min_len <= field_length <= max_len


    def getValidationErrors(self, field_map: dict, is_signup: bool = False):
        """
        Performs validation for authentication forms (Login/Signup).
        Returns a tuple of (is_valid, error_dictionary).
        """
        errors = []
        invalid_widgets = []

        for name, widget in field_map.items():
            # Validation for First and Last Names
            if name in ["first_name", "last_name"]:
                if not self.checkLength(widget, min_len=3, max_len=50):
                    errors.append(f"{name.replace('_', ' ')} must be at least 3 characters")
                    invalid_widgets.append(widget)
                elif not self.validateName(widget):
                    errors.append(f"{name.replace('_', ' ')} format is invalid. Please use only English or Persian letters")
                    invalid_widgets.append(widget)

            # Validation for Nicknames
            if name == "nickname":
                if not self.checkLength(widget, min_len=3, max_len=255):
                    errors.append("nickname must be at least 3 characters")
                    invalid_widgets.append(field_map.get("nickname"))
                elif not self.validateNickname(widget):
                    errors.append("nickname format is invalid, Please use only English or Persian letters")
                    invalid_widgets.append(widget)

            # Validation for Passwords
            elif name == "email":
                if self.validateEmailField(widget) is False:
                    errors.append("email format is invalid")
                    invalid_widgets.append(widget)

            # Validation for Passwords
            elif name == "password":
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


    def getValidatedData(self, field_map: dict):
        """Retrieves and cleans data from fields after successful validation."""
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


    def validateTaskFields(self, task_name_field: QWidget):
        """Validates task titles and descriptions allowing alphanumeric and Persian characters."""
        task_name = self.getFieldText(task_name_field)
        clean_task_name = " ".join(task_name.split())

        pattern = r"^[a-zA-Z\d\u0600-\u06FF\s]+$"
        if not re.match(pattern, clean_task_name):
            return False

        return clean_task_name


    def validatePriority(self, priority_field: QWidget):
        """Maps priority string to its corresponding integer index."""
        priority = priority_field.currentText()
        valid_priorities = ["Low", "Medium", "High"]
        if priority not in valid_priorities:
            return False

        return valid_priorities.index(priority)


    def getValidatedTaskData(self, field_map: dict):
        """Retrieves and cleans data from fields after successful validation."""
        validated = {}
        for name, widget in field_map.items():
            if name in ["title", "description"]:
                validated[name] = self.validateTaskFields(widget)
            elif name == "priority":
                validated[name] = self.validatePriority(widget)
            else:
                validated[name] = self.getFieldText(widget)
        return validated


    def getTaskModalsValidationErrors(self, field_map: dict):
        """Validates inputs for task-related modal windows."""
        errors = []
        invalid_widgets = []

        for name, widget in field_map.items():
            if name in ["title", "description"]:
                if not self.checkLength(widget, min_len=3, max_len=50):
                    errors.append(f"{name} must be at least 3 characters")
                    invalid_widgets.append(widget)
                elif not self.validateTaskFields(widget):
                    errors.append(f"{name} format is invalid")
                    invalid_widgets.append(widget)

        if errors:
            return False, {"errors": errors, "invalid_widgets": invalid_widgets}
        return True, None
