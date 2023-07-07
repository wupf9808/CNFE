from CNFE.quad.cipher import CT, PK, REG, Cipher
from CNFE.quad.params import PublicParameter


class DataOwner:
    def __init__(self, param: PublicParameter, pk: PK) -> None:
        self.cipher = Cipher(param)
        self.pk = pk

    def encrypt(self, x, reg: REG) -> CT:
        return self.cipher.encrypt(self.pk, x, reg)
