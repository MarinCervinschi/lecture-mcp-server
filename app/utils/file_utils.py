import base64
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

try:
    import magic

    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logger.warning("python-magic not available. MIME type detection will be limited.")


class FileValidationError(Exception):
    """Raised when file validation fails."""

    pass


def decode_file_data(file_data: str | bytes) -> bytes:
    """
    Decode file data from base64 string or return bytes as-is.

    Args:
        file_data: Base64 encoded string or raw bytes

    Returns:
        bytes: Decoded file content

    Raises:
        FileValidationError: If decoding fails
    """
    try:
        if isinstance(file_data, str):
            return base64.b64decode(file_data)
        elif isinstance(file_data, bytes):
            return file_data
        else:
            raise FileValidationError(
                f"Invalid file_data type: {type(file_data)}. Expected str or bytes"
            )
    except Exception as e:
        logger.error(f"Failed to decode file data: {str(e)}")
        raise FileValidationError(f"Failed to decode file data: {str(e)}")


def validate_file_size(file_data: bytes, max_size: Optional[int] = None) -> None:
    """
    Validate file size.

    Args:
        file_data: File content as bytes
        max_size: Maximum allowed size in bytes (uses settings default if None)

    Raises:
        FileValidationError: If file is too large
    """
    max_size = max_size or settings.MAX_FILE_SIZE
    file_size = len(file_data)

    if file_size > max_size:
        raise FileValidationError(
            f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)"
        )

    if file_size == 0:
        raise FileValidationError("File is empty")

    logger.debug(f"File size validated: {file_size} bytes")


def validate_pdf_signature(file_data: bytes) -> None:
    """
    Validate PDF file signature.

    Args:
        file_data: File content as bytes

    Raises:
        FileValidationError: If not a valid PDF
    """
    if not file_data.startswith(b"%PDF-"):
        raise FileValidationError("Invalid PDF file: missing PDF signature")

    if b"%%EOF" not in file_data:
        logger.warning("PDF file may be corrupted: missing EOF marker")

    logger.debug("PDF signature validated")


def detect_mime_type(file_data: bytes) -> str:
    """
    Detect MIME type of file data.

    Args:
        file_data: File content as bytes

    Returns:
        str: Detected MIME type
    """
    if not MAGIC_AVAILABLE:
        logger.debug("python-magic not available, using basic detection")
        if file_data.startswith(b"%PDF-"):
            return "application/pdf"
        return "application/octet-stream"

    try:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(file_data)
        logger.debug(f"Detected MIME type: {mime_type}")
        return mime_type
    except Exception as e:
        logger.warning(f"Failed to detect MIME type: {str(e)}")
        return "application/octet-stream"


def validate_mime_type(file_data: bytes, expected_mime: str) -> None:
    """
    Validate file MIME type.

    Args:
        file_data: File content as bytes
        expected_mime: Expected MIME type

    Raises:
        FileValidationError: If MIME type doesn't match
    """
    if not MAGIC_AVAILABLE:
        logger.warning("python-magic not available, skipping MIME type validation")
        return

    detected_mime = detect_mime_type(file_data)

    if detected_mime != expected_mime:
        raise FileValidationError(
            f"Invalid file type: expected {expected_mime}, got {detected_mime}"
        )

    logger.debug(f"MIME type validated: {detected_mime}")


def validate_file(
    file_data: str | bytes,
    mime_type: Optional[str] = None,
    max_size: Optional[int] = None,
    strict_mime: bool = True,
) -> bytes:
    """
    Validate and decode file data.

    Args:
        file_data: Base64 encoded string or raw bytes
        mime_type: Expected MIME type (e.g., 'application/pdf')
        max_size: Maximum file size in bytes
        strict_mime: If True, validate MIME type strictly (requires python-magic)

    Returns:
        bytes: Validated and decoded file content

    Raises:
        FileValidationError: If validation fails
    """
    decoded_data = decode_file_data(file_data)

    validate_file_size(decoded_data, max_size)

    if mime_type == "application/pdf":
        validate_pdf_signature(decoded_data)

        if strict_mime and MAGIC_AVAILABLE:
            validate_mime_type(decoded_data, mime_type)
        elif strict_mime and not MAGIC_AVAILABLE:
            logger.warning("Strict MIME check requested but python-magic not available")

    logger.info(f"File validated successfully: {len(decoded_data)} bytes")
    return decoded_data
