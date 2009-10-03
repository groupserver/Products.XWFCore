class ValidationError(Exception):
    pass
    
def validate_email(email):
    email_parts = email.split('@')
    if len(email_parts) != 2:
        raise ValidationError("Email address was not valid, did not contain '@'")
    elif len(email_parts[1].split('.')) < 2:
        raise ValidationError("Email address contained an invalid domain")

    return email