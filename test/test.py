import glob
import os.path
import tempfile

import PIL.Image

from src.utils import load_textures, process_textures

def test_noudims():
    with tempfile.TemporaryDirectory() as outdir:
        textures = load_textures("./data/noudim/*.png")
        assert len(textures) == 12

        udims = process_textures(textures)
        assert len(udims) == 1

        for udim in udims.values():
            udim.write_to(outdir)

        for file in glob.glob(f"{outdir}/*.png"):
            print("Checking", file)
            filename = os.path.basename(file);
            good = os.path.join("./good/noudim", filename)

            assert os.path.exists(file)
            assert os.path.exists(good)

            with PIL.Image.open(file) as f, PIL.Image.open(good) as g:
                assert f.size == g.size
                assert f.mode == g.mode

                # Ensure textures are pixel-perfect
                (width, height) = g.size
                for x in range(width):
                    for y in range(height):
                        assert f.getpixel((x, y)) == g.getpixel((x, y))

def test_udims():
    with tempfile.TemporaryDirectory() as outdir:
        textures = load_textures("./data/udim/*.png")
        assert len(textures) == 12

        udims = process_textures(textures)
        assert len(udims) == 1

        for udim in udims.values():
            udim.write_to(outdir)

        for file in glob.glob(f"{outdir}/*.png"):
            print("Checking", file)
            filename = os.path.basename(file);
            good = os.path.join("./good/udim", filename)

            assert os.path.exists(file)
            assert os.path.exists(good)

            with PIL.Image.open(file) as f, PIL.Image.open(good) as g:
                assert f.size == g.size
                assert f.mode == g.mode

                # Ensure textures are pixel-perfect
                (width, height) = g.size
                for x in range(width):
                    for y in range(height):
                        assert f.getpixel((x, y)) == g.getpixel((x, y))