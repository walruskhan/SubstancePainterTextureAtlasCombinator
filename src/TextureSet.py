from PIL import Image
from returns.result import Result, Success, Failure
from src.Texture import Texture
from src.IdMap import IdMap
import os

class TextureSet:
    '''
    A collection of textures to combine into a single atlas
    e.g. All diffuse/glossiness textures for a single UDIM
    '''
    def __init__(self, type):
        self._textures: dict[str, list(Texture)] = {} # a dictionary of materials -> textures (e.g. [body,id], [head,id])
                                                      # we use t.name_minus_type as the key because it handles UDIMS / other stuff succinctly
        self._type = type
        self._udim = None
        self._size = None

    def __repr__(self):
        return f"<TextureSet type='{self.type}' udim='{self._udim}' count='{len(self._textures.keys())}' />"

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

        if self._udim is not None and t.udim != self._udim:
            raise Exception("Cannot add texture with different udim ident than textureset")

        # Ensure textures have the same size (e.g. all diffuse textures should be the same size)
        if self._size is None:
            self._size = t.size
        else:
            if t.size != self._size:
                raise Exception("Cannot add texture with different size than textureset")

        if self._udim is None:
            self._udim = t.udim

        # Create sub-list for this material if it doesn't exist
        if t.nominal_name not in self._textures:
            self._textures[t.nominal_name] = []

        self._textures[t.nominal_name].append(t)

    def write_to(self, idmaps, outdir, udim=None):
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

                                    if type(pixel) is tuple and pixel[2] == 0:
                                        continue

                                    if type(pixel) is int and pixel == 0:
                                        continue

                                    outfile.putpixel((x, y), texturefile.getpixel((x, y)))

            udim_segment = f".{udim}" if udim else ""
            path = os.path.join(outdir, f"{self._type}{udim_segment}.png")
            print(f"Wrote {path}")
            outfile.save(path)

def find_idmap(idmaps, nominal_name) -> Result[IdMap, None]:
    for idmap in idmaps:
        if idmap.nominal_name == nominal_name:
            return Success(idmap)
    return Failure(None)