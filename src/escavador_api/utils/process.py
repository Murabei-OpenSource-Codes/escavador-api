"""Module for process utilitie functions."""
import re
from escavador_api.exceptions import EscavadorAPIInvalidDocumentException


def validate_process_number(process_number: str | int) -> str:
    """Return the 20 digits of a CNJ process number.

    Punctuation is ignored. The two verification digits are not
    checked here. Escavador accepts or rejects the number.

    Args:
        process_number (str | int):
            Process number to validate. Pass a string when the number
            has leading zeros. An integer drops them.

    Returns:
        str:
            Twenty digits of the CNJ number.

    Raises:
        EscavadorAPIInvalidDocumentException:
            If the value is not a string or an integer, or does not
            contain exactly 20 digits.
    """
    # Checks if process_number is a string or int
    if not isinstance(process_number, (str, int)):
        msg = "Process number must be a string or an integer"
        raise EscavadorAPIInvalidDocumentException(
            message=msg,
            payload={"process_number": process_number})

    process_number = str(process_number)
    digits = [int(digit) for digit in process_number if digit.isdigit()]

    if len(digits) != 20:
        msg = "Process number is not in a valid CNJ format"
        raise EscavadorAPIInvalidDocumentException(
            message=msg,
            payload={"process_number": process_number})

    digits = "".join(str(num) for num in digits)
    return digits


def format_process_number(process_number: str) -> str:
    """Format process number to CNJ format.

    Args:
        process_number (str):
            Process number to be formatted.

    Returns:
        str: Formatted process number.
    """
    process_number = re.sub(r'\D', '', process_number)
    formatted_process_number = (
        process_number[0:7] + "-" +
        process_number[7:9] + "." +
        process_number[9:13] + "." +
        process_number[13] + "." +
        process_number[14:16] + "." +
        process_number[16:20])
    return formatted_process_number
