from CNFE.quad.cipher import Cipher
from CNFE.quad.params import PublicParameter


class User:
    def __init__(self, param: PublicParameter) -> None:
        self.cipher = Cipher(param)

    def query(self, a, ct, sk) -> int:
        return self.cipher.decrypt(a, ct, sk)
