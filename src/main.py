import glob
import os
import re
from PIL import Image
from returns.result import Result, Success, Failure
import argparse
from typing import Self

groupregex = re.compile(u'.*_(diffuse|basecolor|normal|height|specular|glossiness).*', re.IGNORECASE)
idregex = re.compile(u'.*(id).*', re.IGNORECASE)
udimregex = re.compile(u'(\d{4}|u\d+_v\d+)\.', re.IGNORECASE)

class Texture:
    def __init__(self, filename: str):
        self.filename = filename

        type = self._get_texture_type(filename)
        if type is Failure:
            raise Exception("Failed to get texture type")

        self.type = type.unwrap()[0]
        self.groupname = type.unwrap()[1]

        m = udimregex.match(filename)
        self.udim = m.group(1) if m else None

        self._size = None
        self._idmap = None

    @property
    def normalized_name(self) -> str:
        return self.filename.replace(self.groupname, "")

    @property
    def size(self) -> (int, int):
        if not self._size:
            with Image.open(self.filename) as file:
                self._size = file.size

        return self._size

    def _get_texture_type(self, filename: str) -> Result[(str, str), None]:
        m = idregex.match(filename)
        if m:
            return Success(("idmap", m.group(1)))

        m = groupregex.match(filename)
        if m:
            return Success((m.group(1), m.group(1)))

        return Failure(None)

    @property
    def idmap(self):
        return self._idmap

    def find_idmap(self, idmaps):
        if self.type == "idmap":
            return None

        for idmap in idmaps:
            if self.normalized_name == idmap.normalized_name and idmap.type == "idmap":
                self._idmap = idmap
                return self._idmap

        return None

def get_input_files(fileglob: str) -> list[str]:
    return glob.glob(fileglob, recursive=True, include_hidden=True)

def make_sets(filenames: list[str]) -> dict[str, list[Texture]]:
    groups = {}
    idmaps = []

    # find all textures and sort into idmap/other
    for filename in filenames:
        t = Texture(filename)
        match t.type:
            case "idmap":
                idmaps.append(t)
                continue
            case _:
                if t.groupname not in groups:
                    groups[t.groupname] = []
                groups[t.groupname].append(t)

    # Associate each texture with it's idmap
    for (groupname, textures) in groups.items():
        for texture in textures:
            idmap = texture.find_idmap(idmaps)

            if not idmap:
                raise f"Could not find idmap for {texture.filename}"

    return groups

def get_size(textures: list[Texture]) -> Result[(int, int), None]:
    sizes = []
    for texture in textures:
        sizes.append(texture.size)
        if texture.idmap:
            sizes.append(texture.idmap.size)

    if len(set(sizes)) != 1:
        return Failure(None)

    return Success(sizes[0])

def combine(textures: list[Texture], fname: str, outdir: str) -> Result(list[str]):
    size = get_size(textures)
    if size is Failure:
        return Failure(None)

    with Image.new("RGB", size.unwrap(), (0, 0, 0)) as outfile:
        for curr in textures:
            (width, height) = curr.idmap.size

            with Image.open(curr.filename) as texture:
                with Image.open(curr.idmap.filename) as idmap:
                    # When idmap pixel is not black, blit pixel from texture to output
                    for y in range(height):
                        for x in range(width):
                            pixel = idmap.getpixel((x, y))
                            if pixel[2] == 0:
                                continue

                            outfile.putpixel((x, y), texture.getpixel((x, y)))

        path = os.path.join(outdir, f"{fname}.png")
        outfile.save(path)

        return Success(path)

def start(fileglob: str, outdir: str):
    os.makedirs(outdir, exist_ok=True)

    filenames = get_input_files(fileglob)
    sets = make_sets(filenames)
    print(sets)

    for (groupname, textures) in sets.items():
        print(combine(textures, groupname, outdir))

def main():
    parser = argparse.ArgumentParser(description='Combine textures from multiple maps into a single texture')
    parser.add_argument('input', metavar='input', type=str, help='glob to find files')
    parser.add_argument('outdir', metavar='outdir', type=str, help='output directory')
    args = parser.parse_args()

    start(args.input, args.outdir)

if __name__ == '__main__':
    main()
