import os
import argparse

from src.utils import load_textures, process_textures


def start(fileglob: str, outdir: str):
    os.makedirs(outdir, exist_ok=True)

    textures = load_textures(fileglob)
    udims = process_textures(textures)

    for udim in udims.values():
        udim.write_to(outdir)

def main():
    parser = argparse.ArgumentParser(description='Combine textures from multiple maps into a single texture')
    parser.add_argument('input', metavar='input', type=str, help='glob to find files')
    parser.add_argument('outdir', metavar='outdir', type=str, help='output directory')
    args = parser.parse_args()

    start(args.input, args.outdir)

if __name__ == '__main__':
    main()
