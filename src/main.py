import glob
import os
import re
from PIL import Image
from returns.result import Result, Success, Failure
import argparse

groupregex = re.compile(u'.*_(diffuse|basecolor|normal|height|specular|glossiness).*', re.IGNORECASE)
idregex = re.compile(u'.*(id).*', re.IGNORECASE)

def get_input_files(fileglob: str) -> list[str]:
    return glob.glob(fileglob, recursive=True, include_hidden=True)

def get_texture_type(filename: str) -> Result[(str, str), None]:
    m = idregex.match(filename)
    if m:
        return Success(("idmap", m.group(1)))

    m = groupregex.match(filename)
    if m:
        return Success((m.group(1), m.group(1)))

    return Failure(None)

def make_sets(filenames: list[str]) -> dict[str, list[(str, str)]]:
    groups = {}
    idmaps = []
    idmap_name = None

    # find all textures and sort into idmap/other
    for filename in filenames:
        type = get_texture_type(filename)
        match type:
            case Success(("idmap", name)):
                idmaps.append(filename)
                idmap_name = name
                continue
            case Success((type, name)):
                if name not in groups:
                    groups[name] = []
                groups[name].append(filename)
                continue
            case _:
                print(f"Failed to match {filename}")

    matched_groups = {}

    # match idmaps to textures
    normalized_idmapnames = [(x.replace(idmap_name, ""), x) for x in idmaps] # tuple of normalized (name without type) and actual filename
    for (groupname, filenames) in groups.items():
        normalized_filenames = [(x.replace(groupname, ""), x) for x in filenames] # tuple of normalized (name without type) and actual filename

        for (idmap_normalized, idmap_name) in normalized_idmapnames:
            for (texture_normalized, texture_name) in normalized_filenames:
                if idmap_normalized == texture_normalized:
                    if groupname not in matched_groups:
                        matched_groups[groupname] = []

                    matched_groups[groupname].append((idmap_name, texture_name))

    return matched_groups

def get_size(filesnames: list[str]) -> Result[(int, int), None]:
    sizes = []
    for filename in filesnames:
        with Image.open(filename) as file:
            sizes.append(file.size)

    if not len(set(sizes)) == 1:
        return Failure(None)

    return Success(sizes[0])

def combine(filenames: list[(str, str)], fname: str, outdir: str) -> Result(list[str]):
    size = get_size([x[1] for x in filenames])
    if size is Failure:
        return Failure(None)

    with Image.new("RGB", size.unwrap(), (0, 0, 0)) as outfile:

        for (idmap, filename) in filenames:
            with Image.open(idmap) as idmap:
                (width, height) = idmap.size

                with Image.open(filename) as texture:
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

    for (groupname, filenames) in sets.items():
        print(combine(filenames, groupname, outdir))

def main():
    parser = argparse.ArgumentParser(description='Combine textures from multiple maps into a single texture')
    parser.add_argument('input', metavar='input', type=str, help='glob to find files')
    parser.add_argument('outdir', metavar='outdir', type=str, help='output directory')
    args = parser.parse_args()

    start(args.input, args.outdir)

if __name__ == '__main__':
    main()
