import numpy as np
import cv2
import click
from pathlib import Path
from utils import draw_contour, get_vector, get_contour
import mercantile


@click.command(short_help="Get range color from images")
@click.option(
    "--img_file",
    help="Imagen file",
    type=str,
    default="./../fixture/141155-193764-19.jpeg",
)
def main(img_file):
    # Get path for output image
    img = cv2.imread(img_file)
    img_path = Path(img_file)
    output_img_path = f"{img_path.parent}/{img_path.stem}_output{img_path.suffix}"
    geojson_output = f"{img_path.parent}/{img_path.stem}.geojson"

    # Get bbox for image file
    tile = list(map(int, img_path.stem.split("-")))
    img_bbox = mercantile.bounds(tile[0], tile[1], tile[2])

    tree_canopy = {
        "key": "tree",
        "lower": [33, 44, 88],
        "upper": [97, 131, 164],
        "area": [1000, 10000],
        "kernel": (3, 3),
    }

    contours = get_contour(
        img,
        tree_canopy["lower"],
        tree_canopy["upper"],
        tree_canopy["area"],
        tree_canopy["kernel"],
    )

    # Draw contour in the image
    draw_contour(img, contours, output_img_path)
    # Get vector data from contour
    get_vector(img, img_bbox, contours, geojson_output)


if __name__ == "__main__":
    main()
