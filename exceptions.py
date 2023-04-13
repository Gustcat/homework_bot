class InterceptRequestException(Exception):
    """Класс исключения для перехвата requests.RequestException."""

    pass


class JSONError(TypeError):
    """
    Класс исключения.
    Возникает при невозможности сериализации JSON.
    """

    pass


class APITypeError(TypeError):
    """
    Класс исключения.
    Указывает на то, что API структура данных не словарь.
    """

    pass


class APIKeyError(KeyError):
    """
    Класс исключения.
    Указывает на отсутствие ключа "homeworks" в ответе API.
    """

    pass
