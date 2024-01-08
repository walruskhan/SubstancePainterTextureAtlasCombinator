from src.TextureSet import TextureSet
from src.Texture import Texture
from returns.result import Result, Success, Failure

class UDIM:
    '''
    A UDIM holds texturesets which contains textures
    '''
    def __init__(self):
        self._texturesets: dict[str, TextureSet] = {}
        self.idmaps = []
        self.udim = None

    def add(self, texture: Texture) -> Result[Texture, None]:
        # Ensure UDIMs match
        if self.udim is None:
            self.udim = texture.udim
        elif self.udim != texture.udim:
            return Failure(None)

        if texture.is_idmap:
            self.idmaps.append(texture)
            return Success(texture)

        if texture.type not in self._texturesets:
            self._texturesets[texture.type] = TextureSet(texture.type)

        self._texturesets[texture.type].add(texture)
        return Success(texture)

    def write_to(self, outdir):
        for (type, textureset) in self._texturesets.items():
            textureset.write_to(self.idmaps, outdir, udim=self.udim)