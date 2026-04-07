from rest_framework import status
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    fields = {}
    message = 'Request failed.'

    normalized_data = _normalize_data(response.data)
    if isinstance(normalized_data, dict):
        field_like = {
            key: value
            for key, value in normalized_data.items()
            if key not in {'detail', 'message', 'status', 'error'}
        }
        if field_like:
            fields = field_like
        message = (
            _extract_first_string(normalized_data.get('detail'))
            or _extract_first_string(normalized_data.get('message'))
            or _extract_first_string(normalized_data.get('non_field_errors'))
            or _extract_first_string(normalized_data)
            or _default_message_for_status(response.status_code)
        )
    elif isinstance(normalized_data, list):
        fields = {'non_field_errors': normalized_data}
        message = _extract_first_string(normalized_data) or _default_message_for_status(response.status_code)
    elif isinstance(normalized_data, str):
        message = normalized_data
    else:
        message = _default_message_for_status(response.status_code)

    error_payload = {
        'message': message,
        'status': response.status_code,
        'fields': fields,
    }

    response.data = {
        'error': error_payload,
        'detail': message,
        'message': message,
        'fields': fields,
        **fields,
    }
    return response


def _normalize_data(data):
    if isinstance(data, dict):
        return {key: _normalize_data(value) for key, value in data.items()}
    if isinstance(data, list):
        return [_normalize_data(item) for item in data]
    return str(data)


def _extract_first_string(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        for item in value:
            nested = _extract_first_string(item)
            if nested:
                return nested
        return None
    if isinstance(value, dict):
        for item in value.values():
            nested = _extract_first_string(item)
            if nested:
                return nested
    return None


def _default_message_for_status(status_code):
    defaults = {
        status.HTTP_400_BAD_REQUEST: 'Validation failed.',
        status.HTTP_401_UNAUTHORIZED: 'Authentication required.',
        status.HTTP_403_FORBIDDEN: 'You do not have permission to perform this action.',
        status.HTTP_404_NOT_FOUND: 'Resource not found.',
        status.HTTP_429_TOO_MANY_REQUESTS: 'Too many requests.',
        status.HTTP_500_INTERNAL_SERVER_ERROR: 'Internal server error.',
    }
    return defaults.get(status_code, 'Request failed.')
