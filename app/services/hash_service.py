from passlib.context import CryptContext


class HashService:
    crypt_context: CryptContext

    def __init__(
        self,
        crypt_context: CryptContext
    ):
        self.crypt_context = crypt_context

    def hash_password(
        self,
        plain_password: str
    ) -> str:
        return self.crypt_context.hash(plain_password)
    
    def verify_password(
        self,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        return self.crypt_context.verify(
            plain_password,
            hashed_password
        )
