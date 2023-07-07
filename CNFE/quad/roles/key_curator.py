from CNFE.quad.cipher import PK, REG, SK, Cipher
from CNFE.quad.params import PublicParameter


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

    def keygen(self, a, reg) -> SK:
        return self.cipher.keygen(self.pk, self.msk, a, self.sigma, reg)
