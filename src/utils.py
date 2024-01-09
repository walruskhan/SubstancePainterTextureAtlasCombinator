import glob

from src.Texture import Texture
from src.UDIM import UDIM

def load_textures(fileglob: str) -> list[Texture]:
    files = glob.glob(fileglob, recursive=True, include_hidden=True)
    return [Texture(f) for f in files]

def process_textures(textures: list[Texture]) -> dict[str|None, UDIM]:
    idmaps = []
    udims = {}

    for texture in textures:
        match texture.type:
            case "idmap":
                idmaps.append(texture)
            case _:
                if texture.udim not in udims:
                    udims[texture.udim] = UDIM()
                udims[texture.udim].add(texture)

    for idmap in idmaps:
        udims[idmap.udim].add(idmap)

    return udims