from api.helpers.request_validator import (
    BodyRequestValidator,
    FilesRequestValidator,
    QueryRequestValidator,
    RequestValidatorTypes,
)


class VerificationStatus:
    Pending = "pending"
    Success = "true"
    Fail = "false"


class Environment:
    TEST = "test"
    DEVELOPMENT = "development"
    PRODUCTION = "production"


REQUEST_VALIDATOR_CLASSES = {
    RequestValidatorTypes.Body: BodyRequestValidator,
    RequestValidatorTypes.Query: QueryRequestValidator,
    RequestValidatorTypes.Files: FilesRequestValidator,
}

DEFAULT_LIMIT = 50
