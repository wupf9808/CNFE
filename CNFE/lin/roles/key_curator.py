from CNFE.lin.cipher import PK, REG, SK, Cipher
from CNFE.lin.params import PublicParameter


class KeyCurator:
    def __init__(self, param: PublicParameter, sigma) -> None:
        self.cipher = Cipher(param)
        self.pk, self.msk = self.cipher.setup()
        self.sigma = sigma

    @property
    def pubkey(self) -> PK:
        return self.pk

    def register(self) -> REG:
        return self.cipher.datareg()

    def keygen(self, y, reg) -> SK:
        return self.cipher.keygen(self.msk, y, self.sigma, reg)
