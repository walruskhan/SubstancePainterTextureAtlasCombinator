import logging

from src.common import groupregex, udimregex
from PIL import Image

# Represents a handle to a texture file
class Texture:
    def __init__(self, filename: str):
        self.filename = filename
        self._logger = logging.getLogger(self.__class__.__name__)

        m = groupregex.match(filename)
        if not m:
            self._logger.error(f"Failed to get texture type {filename}")
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