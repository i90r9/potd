import hashlib
import string


def compute_hash(value):
    return hashlib.sha256(
        str.encode(
            value.lower().translate(
                str.maketrans(
                    "",
                    "",
                    string.punctuation,
                )
            )
        )
    ).hexdigest()
