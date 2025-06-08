"""
Dùng để load error code mapping theo từng API module.
Sau này chỉ cần import đúng module theo API group là xong.
"""

from error_mapping import (
    authenticate_provider,
    gbizid_authenticate_user,
    submit_application_set,
    reference_number
)

ERROR_MAPPING = {
    "authenticate_provider": authenticate_provider.AUTHENTICATE_PROVIDER_ERROR_MAPPING,
    "gbizid_authenticate_user": gbizid_authenticate_user.GBIZID_AUTH_USER_ERROR_MAPPING,
    "submit_application_set": submit_application_set.SUBMIT_APPLICATION_ERROR_MAPPING,
    "reference_number": reference_number.REFERENCE_NUMBER_ERROR_MAPPING
}
