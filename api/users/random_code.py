import random

def _uuid_generator(length=8):
    while True:
        random_string = ''
        random_str_seq = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        for i in range(0, length):
            random_string += str(random_str_seq[random.randint(0, len(random_str_seq) - 1)])
        yield random_string


#
# Generate an 8 character long random string generator
#
UUID_8 = _uuid_generator(length=8)


def get_uuid_8():
    """
    Returns an 8 character long uuid.
    :return: 8 character long uuid.
    """
    return next(UUID_8)