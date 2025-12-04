XY_FILE = "coords/coords_xy.txt"
ZY_FILE = "coords/coords_zy.txt"
OUT_FILE = "coords/coords_3d.txt"

def read_coords(fname):
    with open(fname) as f:
        return [tuple(map(int, line.split(","))) 
                for line in f if line.strip()]

xy = read_coords(XY_FILE)
zy = read_coords(ZY_FILE)

# makes sure xy and zy files have same number of coords
if len(xy) != len(zy):
    raise ValueError("XY and ZY files must have same number of lines")

with open(OUT_FILE, "w") as out:
    for (x, y1), (z, y2) in zip(xy, zy):
        y = int((y1 + y2) / 2)                # average of two y values
        out.write(f"{x},{y},{z}\n")

print("Created:", OUT_FILE)
