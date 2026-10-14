from pathlib import Path
DATASET_DIR = Path("dataset")
SPLITS = ("train", "val")
IMAGE_EXTENSIONS ={".jpg",".jpeg",".png",".bmp",".webp"}
def get_images(directory:Path)-> set[str]:
    """Return image filenames without their extensions"""
    return{
        path.stem
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    }
def get_labels(directory: Path) -> set[str]:
    """Return label filenemaes without their extensions"""
    return {
        path.stem
        for path in directory.glob("*.txt")
        if path.is_file()
    }
def main () -> None:
    has_errors = False
    for split in SPLITS:
        image_dir = DATASET_DIR/ "images"/split
        label_dir = DATASET_DIR/"labels" / split
        if not image_dir.is_dir() or not label_dir.is_dir():
            print(f"ERROR:Missing directory for {split}")
            has_errors = True
            continue
        images = get_images(image_dir)
        labels = get_labels(label_dir)
        missing_labels = sorted(images - labels)
        orphan_labels = sorted(labels - images)
        print(f"\n{split.upper()}")
        print(f"Images:{len(images)}")
        print(f"Labels:{len(labels)}")

        if missing_labels:
            print("Images missing labels:", missing_labels)
            has_errors = True

        if orphan_labels:
            print("Labels missing images:", orphan_labels)
            has_errors = True

        if not missing_labels and not orphan_labels:
            print("Image-label pairing: OK")
    if has_errors:
        raise SystemExit("DATASET CHECK FAILED")
    print("\nDATASET PAIRING CHECK PASSED")


if __name__ == "__main__":
    main()



