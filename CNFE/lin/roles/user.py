from CNFE.lin.cipher import Cipher
from CNFE.lin.params import PublicParameter


class User:
    def __init__(self, param: PublicParameter) -> None:
        self.cipher = Cipher(param)

    def query(self, ct, sk) -> int:
        return self.cipher.decrypt(ct, sk)
