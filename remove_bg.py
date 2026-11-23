#!/usr/bin/env python3
"""Recursively remove backgrounds from images and save them as transparent PNGs.

Setup:
    pip install "rembg[cpu]" pillow        # or "rembg[gpu]" if you have CUDA

Usage:
    python remove_bg.py            (uses the "pictures" folder next to the script)
    python remove_bg.py INPUT_DIR [OUTPUT_DIR] [--model M] [--upscale 2] [--sharpen 0] [--overwrite]

The folder structure of INPUT_DIR is mirrored into OUTPUT_DIR
(default: INPUT_DIR + "_nobg"). Originals are never modified.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image

EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def enhance(img, upscale, sharpen):
    """Upscale + sharpen the colors only; the transparency (alpha) is resized
    separately and left unsharpened so edges stay clean."""
    from PIL import ImageFilter
    if upscale and upscale != 1.0:
        size = (round(img.width * upscale), round(img.height * upscale))
        img = img.resize(size, Image.LANCZOS)
    if sharpen > 0:
        r, g, b, a = img.split()
        rgb = Image.merge("RGB", (r, g, b)).filter(
            ImageFilter.UnsharpMask(radius=1.6, percent=int(110 * sharpen), threshold=2))
        img = Image.merge("RGBA", (*rgb.split(), a))
    return img


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", type=Path, nargs="?",
                   default=Path(__file__).resolve().parent / "pictures",
                   help="folder with images (default: the 'pictures' folder next to this script)")
    p.add_argument("output", type=Path, nargs="?")
    p.add_argument("--model", default="isnet-general-use",
                   help="isnet-general-use (default), u2net, u2netp (fast), "
                        "isnet-anime, birefnet-general, silueta ...")
    p.add_argument("--upscale", type=float, default=1.0,
                   help="enlarge output by this factor, e.g. 2 (default 1 = no change)")
    p.add_argument("--sharpen", type=float, default=1.0,
                   help="sharpening strength, 0 = off, 1 = normal, 2 = strong (try 1)")
    p.add_argument("--overwrite", action="store_true", help="re-process files that already exist in output")
    args = p.parse_args()

    src = args.input.resolve()
    if not src.exists():
        src.mkdir(parents=True)
        sys.exit(f"Created the input folder: {src}\nPut your pictures in it and run the script again.")
    if not src.is_dir():
        sys.exit(f"Not a folder: {src}")
    dst = (args.output or src.with_name(src.name + "_nobg")).resolve()

    files = [f for f in src.rglob("*")
             if f.is_file() and f.suffix.lower() in EXTS and dst not in f.parents]
    print(f"Found {len(files)} images in {src}", flush=True)
    if not files:
        sys.exit("Nothing to do.")

    print("Importing rembg (can take 30-60s the first time)...", flush=True)
    from rembg import new_session, remove

    print(f"Loading model '{args.model}' (first run downloads ~170MB to ~/.u2net, "
          "please wait)...", flush=True)
    session = new_session(args.model)  # load once, reuse for every image
    print("Model ready. Processing...", flush=True)

    ok = skipped = failed = 0
    for i, f in enumerate(files, 1):
        out = dst / f.relative_to(src).with_suffix(".png")
        if out.exists() and not args.overwrite:
            skipped += 1
            continue
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(f) as im:
                result = remove(im.convert("RGBA"), session=session)
            result = enhance(result, args.upscale, args.sharpen)
            result.save(out, "PNG")
            ok += 1
            print(f"[{i}/{len(files)}] {f.relative_to(src)}", flush=True)
        except Exception as e:  # keep going on a bad file
            failed += 1
            print(f"[{i}/{len(files)}] FAILED {f.relative_to(src)}: {e}", file=sys.stderr)

    print(f"Done. {ok} processed, {skipped} skipped, {failed} failed -> {dst}")


if __name__ == "__main__":
    main()
