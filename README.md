# Usage
1. Configure Substance Painter (or your texturing program) to export textures and an idmap.
2. Run `python3 main.py` in the root directory of this project.

# Substance Painter
## 1: Setup an export template like the following
 
![Screenshot of Substance Painter export settings](misc/substance.png)
Note:
1. There is an idmap exported, which is used to determine which texture belongs to which object.
2. UDIMS (if used) are sorted into folders (and the script needs to be run against each folder separately, no UDIM support yet)

## 2: Run the script
```
python3 main.py ./exampledata/udim/1001/*.png ./mytextures
```
This will spit out a texture for each type of texture (basecolor, normal, etc) in the `mytextures` folder.