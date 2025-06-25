class ValidationError(Exception):
    pass

class BaseModel:
    def __init__(self, **data):
        for k, v in data.items():
            setattr(self, k, v)

class Field:
    def __init__(self, default=None, description=None):
        self.default = default
        self.description = description

class PositiveInt(int):
    pass

def confloat(*, ge=None, le=None, gt=None, lt=None, eq=None):
    return float
