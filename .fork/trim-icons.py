"""Trim the transparent margin baked into the bundled plugin icons.

Several plugin brand icons carry a transparent border inside the file itself
(workbuddy.png and zcode.png are only 83% content). The OAuth cards render icons
with `object-fit: contain`, so that inset shows up as a visible gap around the
artwork, and no CSS can recover it - the pixels have to go.

Usage:
    python trim-icons.py <icons-dir>                 # every png in <dir>
    python trim-icons.py <icons-dir> workbuddy zcode # only the named ones

Scope note: the upstream icon set is deliberately left alone. Trimming it would
resize unrelated provider marks (code0.png is only 57% content), which is a far
larger visual change than this fix needs. A tight image is left untouched, so
naming an already tight icon is harmless.
"""

import glob
import os
import sys

from PIL import Image

ALPHA_THRESHOLD = 8


def trim(path):
    """Crop transparent margins and re-centre on a square canvas.

    Returns (before, after) sizes when the file changed, otherwise None.
    """
    image = Image.open(path).convert("RGBA")
    alpha = image.getchannel("A").point(lambda value: 255 if value > ALPHA_THRESHOLD else 0)
    box = alpha.getbbox()
    if not box or box == (0, 0, image.width, image.height):
        return None

    cropped = image.crop(box)
    # keep the aspect ratio neutral so existing layout rules stay valid
    side = max(cropped.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(cropped, ((side - cropped.width) // 2, (side - cropped.height) // 2))
    canvas.save(path, format="PNG", optimize=True)
    return image.size, canvas.size


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    directory = sys.argv[1]
    wanted = [name[:-4] if name.endswith(".png") else name for name in sys.argv[2:]]

    if wanted:
        paths = [os.path.join(directory, name + ".png") for name in wanted]
        missing = [path for path in paths if not os.path.isfile(path)]
        if missing:
            print("missing icon(s): %s" % ", ".join(os.path.basename(p) for p in missing))
            return 1
    else:
        paths = sorted(glob.glob(os.path.join(directory, "*.png")))

    if not paths:
        print("no png icons found in %s" % directory)
        return 1

    changed = 0
    for path in paths:
        name = os.path.basename(path)
        result = trim(path)
        if result:
            before, after = result
            changed += 1
            print("trim %-16s %dx%d -> %dx%d" % (name, before[0], before[1], after[0], after[1]))
        else:
            print("keep %-16s already tight" % name)

    print("trimmed %d of %d icon(s)" % (changed, len(paths)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
