import glob
import os
import re
from PIL import Image
from returns.result import Result, Success, Failure
import argparse

from src.Texture import Texture
from src.TextureSet import TextureSet
from src.UDIM import UDIM


def load_textures(fileglob: str) -> list[Texture]:
    files = glob.glob(fileglob, recursive=True, include_hidden=True)
    return [Texture(f) for f in files]

def make_texturesets(textures: list[Texture]) -> (dict[str, TextureSet], list[Texture]):
    sets = {}
    idmaps = []

    for texture in textures:
        if texture.type is None:
            raise Exception(f"Failed to get texture type for {texture.filename}")

        # If this is an idmap, add it to the idmap list and continue
        if texture.is_idmap:
            idmaps.append(texture)
            continue

        # If this is not an idmap, add it to the textureset list
        key = (texture.type, texture.udim)
        if texture.type not in sets:
            sets[key] = TextureSet(texture.type)
        sets[key].add(texture)

    return sets, idmaps

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

def start(fileglob: str, outdir: str):
    os.makedirs(outdir, exist_ok=True)

    textures = load_textures(fileglob)
    udims = process_textures(textures)

    for udim in udims.values():
        udim.write_to(outdir)

    # (sets, idmaps) = make_texturesets(textures)
    # print(sets, idmaps)
    #
    # for (_, textureset) in sets.items():
    #     textureset.write_to(idmaps, outdir)

def main():
    parser = argparse.ArgumentParser(description='Combine textures from multiple maps into a single texture')
    parser.add_argument('input', metavar='input', type=str, help='glob to find files')
    parser.add_argument('outdir', metavar='outdir', type=str, help='output directory')
    args = parser.parse_args()

    start(args.input, args.outdir)

if __name__ == '__main__':
    main()
