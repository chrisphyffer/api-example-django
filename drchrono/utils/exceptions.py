class APIException(Exception): pass

class Forbidden(APIException): pass

class NotFound(APIException): pass

class Conflict(APIException): pass