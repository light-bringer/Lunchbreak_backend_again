from rest_framework.versioning import BaseVersioning


class HeaderVersioning(BaseVersioning):
    default_version = '2.0.0'
    allowed_versions = [
        default_version,
        '2.1.0',
        '2.2.0',
        '2.2.1',
        '2.2.2',
        '2.3.0',
    ]

    def determine_version(self, request, *args, **kwargs):
        from .exceptions import UnsupportedAPIVersion
        version = request.META.get(
            'HTTP_X_VERSION',
            HeaderVersioning.default_version
        )
        if version not in self.allowed_versions:
            raise UnsupportedAPIVersion()
        return version
