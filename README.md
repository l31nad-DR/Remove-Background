# Remove-Background

A Python script that removes the background from all pictures in a folder (including subfolders) and saves them as transparent PNGs. It uses the [rembg](https://github.com/danielgatis/rembg) library and can optionally upscale and sharpen the results.

Your original pictures are never modified.

## Install

Requires Python 3.9 or newer.

```
pip install "rembg[cpu]" pillow
```

If you have an NVIDIA GPU with CUDA, use `pip install "rembg[gpu]" pillow` instead for much faster processing.

## Run

1. Put your pictures in a folder named `pictures` next to `remove_bg.py` (the script creates it for you on the first run if it is missing).
2. Run:

```
python remove_bg.py
```

3. The transparent PNGs are saved in `pictures_nobg`, with the same subfolder structure as `pictures`.

On the first run the script downloads the AI model (about 180 MB). This happens once and can take a minute or two.

## Options

| Option | Default | Description |
| --- | --- | --- |
| `input` | `pictures` next to the script | Folder with the images |
| `output` | `<input>_nobg` | Folder for the results |
| `--model` | `isnet-general-use` | Model used. Others: `u2net`, `u2netp` (fast), `isnet-anime` (illustrations), `silueta`, `birefnet-general` (best quality, needs a lot of RAM) |
| `--upscale` | `1` | Enlarge the output, e.g. `2` doubles the size |
| `--sharpen` | `1` | Sharpening strength: `0` off, `1` normal, `2` strong |
| `--overwrite` | off | Re-process images that already exist in the output folder |

Examples:

```
python remove_bg.py "C:\path\to\photos"
python remove_bg.py pictures results --upscale 2
python remove_bg.py --sharpen 0 --overwrite
```

## Notes

- Supported formats: jpg, jpeg, png, webp, bmp, tif, tiff.
- Output is always PNG, because it supports transparency.
- Images that already exist in the output folder are skipped, so you can stop and resume a large batch.
- If an image fails, the script reports it and continues with the rest.
- Upscaling and sharpening are simple resizing and sharpening. They improve edge crispness but cannot add detail that is not in the original picture.
- Results vary by image. If some cutouts have leftover fragments, try a different `--model`.
