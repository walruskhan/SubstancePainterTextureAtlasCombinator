import glob
import os
import re
from PIL import Image
from returns.result import Result, Success, Failure
import argparse

groupregex = re.compile(r'.*_(diffuse|basecolor|normal|height|specular|glossiness|id).*', re.IGNORECASE)
udimregex = re.compile(r'.*(\d{4}|u\d+_v\d+)\.', re.IGNORECASE)

# Represents a handle to a texture file
class Texture:
    def __init__(self, filename: str):
        self.filename = filename

        m = groupregex.match(filename)
        if not m:
            raise Exception(f"Failed to get texture type {filename}")
        self._type = m.group(1)

        m = udimregex.match(filename)
        self.udim = m.group(1) if m else None

        self._size = None

    def __repr__(self):
        return f"<Texture filename='{self.filename}' type='{self.type}' udim='{self.udim}' />"

    @property
    def type(self) -> str:
        '''
        Returns the type of texture this is (e.g. idmap, specular, glossiness, etc.)
        :return: A Success object containing texture type or Failure if type could not be determined
        '''
        return self._type.lower()

    @property
    def is_idmap(self) -> bool:
        '''
        Returns True if this texture is an idmap
        :return: True if this texture is an idmap
        '''
        return self.type in ["idmap", "id"]

    @property
    def nominal_name(self) -> str:
        '''
        Returns the filename of this texture with the type removed
        :return: The filename of this texture with the type removed
        '''
        return self.filename.replace(self._type, "")

    @property
    def size(self):
        if not self._size:
            with Image.open(self.filename) as file:
                self._size = file.size
        return self._size

class IdMap(Texture):
    pass

class TextureSet:
    '''
    A collection of textures to combine into a single atlas
    e.g. All diffuse/glossiness textures for a single UDIM
    '''
    def __init__(self, type):
        self._textures: dict[str, list(Texture)] = {} # a dictionary of materials -> textures (e.g. [body,id], [head,id])
                                                      # we use t.name_minus_type as the key because it handles UDIMS / other stuff succinctly
        self._type = type
        self._size = None

    def __repr__(self):
        return f"<TextureSet type='{self.type}' count='{len(self._textures.keys())}' />"

    @property
    def type(self) -> Result[str, None]:
        '''
        Returns the type of textureset this is (e.g. idmap, specular, glossiness, etc.)
        All contained textures should have this type
        :return: A Success object containing texture type or Failure if type could not be determined
        '''
        return self._type.lower()

    def add(self, t: Texture):
        if self.type is Failure:
            raise Exception("Cannot add texture to textureset with no type")

        if t.type is Failure:
            raise Exception("Cannot add texture with no type")

        if t.type != self._type:
            raise Exception("Cannot add texture with different type than textureset")

        # Ensure textures have the same size (e.g. all diffuse textures should be the same size)
        if self._size is None:
            self._size = t.size
        else:
            if t.size != self._size:
                raise Exception("Cannot add texture with different size than textureset")

        # Create sub-list for this material if it doesn't exist
        if t.nominal_name not in self._textures:
            self._textures[t.nominal_name] = []

        self._textures[t.nominal_name].append(t)

    def write_to(self, idmaps, outdir):
        with Image.new("RGB", self._size, (0, 0, 0)) as outfile:
            for (nominal, textures) in self._textures.items():
                # Get idmap to use with writing current nominal textures
                idmap = find_idmap(idmaps, nominal)
                if idmap is Failure:
                    raise Exception(f"Could not find idmap for {nominal}")
                idmap = idmap.unwrap()

                with Image.open(idmap.filename) as idmapfile:
                    for texture in textures:
                        with Image.open(texture.filename) as texturefile:

                            for y in range(self._size[1]):
                                for x in range(self._size[0]):
                                    pixel = idmapfile.getpixel((x, y))
                                    if pixel[2] == 0:
                                        continue

                                    outfile.putpixel((x, y), texturefile.getpixel((x, y)))

            path = os.path.join(outdir, f"{self._type}.png")
            print(f"Wrote {path}")
            outfile.save(path)

def find_idmap(idmaps, nominal_name) -> Result[IdMap, None]:
    for idmap in idmaps:
        if idmap.nominal_name == nominal_name:
            return Success(idmap)
    return Failure(None)

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
        if texture.type not in sets:
            sets[texture.type] = TextureSet(texture.type)
        sets[texture.type].add(texture)

    return sets, idmaps

def start(fileglob: str, outdir: str):
    os.makedirs(outdir, exist_ok=True)

    textures = load_textures(fileglob)
    (sets, idmaps) = make_texturesets(textures)
    print(sets, idmaps)

    for (_, textureset) in sets.items():
        textureset.write_to(idmaps, outdir)

def main():
    parser = argparse.ArgumentParser(description='Combine textures from multiple maps into a single texture')
    parser.add_argument('input', metavar='input', type=str, help='glob to find files')
    parser.add_argument('outdir', metavar='outdir', type=str, help='output directory')
    args = parser.parse_args()

    start(args.input, args.outdir)

if __name__ == '__main__':
    main()
