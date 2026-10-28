from pathlib import Path

from PIL import Image, ImageOps

RAW = Path("assets/raw")
OUT = Path("assets")
# output name: (width, height) in pixels
SIZES = {"bg": (1920, 1080), "sidebar": (600, 1400), "home": (1600, 400),
         "eda": (1600, 400), "advisor": (1600, 400), "models": (1600, 400)}


def main():
    for name, size in SIZES.items():
        files = list(RAW.glob(f"{name}.*"))
        if not files:
            print("missing:", name)
            continue
        img = Image.open(files[0]).convert("RGB")
        img = ImageOps.fit(img, size, Image.LANCZOS)      # crop + resize to the exact size
        img.save(OUT / f"{name}.jpg", quality=80, optimize=True)
        print("saved", name, size)


if __name__ == "__main__":
    main()