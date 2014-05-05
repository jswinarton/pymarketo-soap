from connection import MarketoConnection


def connect(user_id, location, encryption_key):
    return MarketoConnection(
        user_id,
        location,
        encryption_key,
    )
