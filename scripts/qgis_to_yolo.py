import os
import shutil
import geopandas as gpd
import rasterio
from shapely.geometry import Polygon, MultiPolygon


# ============================================================
# USER SETTINGS
# ============================================================

# Folder containing the GeoTIFF tiles
TILES_FOLDER = r"YOUR_TILES_FOLDER"

# QGIS annotation GeoPackage
ANNOTATION_FILE = r"YOUR_ANNOTATION_FILE.gpkg"

# Output YOLO dataset folder
OUTPUT_FOLDER = r"YOUR_OUTPUT_DATASET_FOLDER"

# Train / Validation ratio
TRAIN_RATIO = 0.8


# ============================================================
# OUTPUT FOLDERS
# ============================================================

TRAIN_IMAGES = os.path.join(
    OUTPUT_FOLDER,
    "images",
    "train"
)

VAL_IMAGES = os.path.join(
    OUTPUT_FOLDER,
    "images",
    "val"
)

TRAIN_LABELS = os.path.join(
    OUTPUT_FOLDER,
    "labels",
    "train"
)

VAL_LABELS = os.path.join(
    OUTPUT_FOLDER,
    "labels",
    "val"
)


for folder in [
    TRAIN_IMAGES,
    VAL_IMAGES,
    TRAIN_LABELS,
    VAL_LABELS
]:
    os.makedirs(folder, exist_ok=True)


# ============================================================
# READ QGIS ANNOTATIONS
# ============================================================

print("===================================")
print("READING QGIS ANNOTATIONS")
print("===================================")

gdf = gpd.read_file(ANNOTATION_FILE)

print(f"Total annotations : {len(gdf)}")
print(f"Annotation CRS    : {gdf.crs}")
print(f"Columns           : {list(gdf.columns)}")
print()


# ============================================================
# CHECK REQUIRED FIELDS
# ============================================================

if "tile_id" not in gdf.columns:
    raise ValueError(
        "ERROR: 'tile_id' field not found in annotation layer."
    )

if "class" not in gdf.columns:
    raise ValueError(
        "ERROR: 'class' field not found in annotation layer."
    )


# ============================================================
# FIND UNIQUE TILES
# ============================================================

tile_ids = sorted(
    gdf["tile_id"]
    .dropna()
    .astype(str)
    .unique()
)

print("Tiles found in annotation:")

for tile_id in tile_ids:
    print(f"  {tile_id}")

print()


# ============================================================
# TRAIN / VALIDATION SPLIT
# ============================================================

if len(tile_ids) == 1:

    train_tiles = tile_ids
    val_tiles = tile_ids

    print("Only one tile found.")
    print(
        "Using the same tile for "
        "train and validation for this trial."
    )

else:

    split_index = max(
        1,
        int(len(tile_ids) * TRAIN_RATIO)
    )

    train_tiles = tile_ids[:split_index]

    val_tiles = tile_ids[split_index:]

    if len(val_tiles) == 0:
        val_tiles = train_tiles


print()
print("Train tiles:")
print(train_tiles)

print()
print("Validation tiles:")
print(val_tiles)

print()


# ============================================================
# POLYGON → YOLO SEGMENTATION
# ============================================================

def polygon_to_yolo(
    polygon,
    transform,
    image_width,
    image_height
):

    if polygon.is_empty:
        return None

    # Exterior boundary
    coords = list(
        polygon.exterior.coords
    )

    normalized_points = []

    for x, y in coords:

        # Geographic coordinate
        # ->
        # Pixel coordinate

        col, row = (
            ~transform
        ) * (x, y)

        # Normalize to 0-1
        x_norm = col / image_width
        y_norm = row / image_height

        # Do NOT silently clip invalid coordinates.
        # This helps detect CRS / geometry problems.

        if not (
            0.0 <= x_norm <= 1.0
            and
            0.0 <= y_norm <= 1.0
        ):
            return None

        normalized_points.extend([
            x_norm,
            y_norm
        ])

    # Need at least 3 points
    if len(normalized_points) < 6:
        return None

    # YOLO segmentation format:
    # class x1 y1 x2 y2 ...

    line = (
        "0 "
        +
        " ".join(
            f"{value:.6f}"
            for value in normalized_points
        )
    )

    return line


# ============================================================
# PROCESS EACH TILE
# ============================================================

print("===================================")
print("CONVERTING ANNOTATIONS")
print("===================================")

total_polygons = 0
skipped_polygons = 0


for tile_id in tile_ids:

    print()
    print(
        f"Processing: {tile_id}"
    )

    # --------------------------------------------------------
    # Find corresponding GeoTIFF
    # --------------------------------------------------------

    tif_path = os.path.join(
        TILES_FOLDER,
        tile_id + ".tif"
    )

    if not os.path.exists(tif_path):

        print(
            "WARNING: Tile not found:"
        )

        print(tif_path)

        continue


    # --------------------------------------------------------
    # Select annotations for this tile
    # --------------------------------------------------------

    tile_gdf = gdf[
        gdf["tile_id"].astype(str)
        == tile_id
    ].copy()


    # --------------------------------------------------------
    # Open raster
    # --------------------------------------------------------

    with rasterio.open(tif_path) as src:

        width = src.width
        height = src.height
        transform = src.transform
        raster_crs = src.crs

        print(
            f"Image size: "
            f"{width} x {height}"
        )

        print(
            f"Raster CRS: {raster_crs}"
        )


        # ----------------------------------------------------
        # Reproject annotations to raster CRS
        # ----------------------------------------------------

        if tile_gdf.crs is None:
            raise ValueError(
                "ERROR: Annotation layer has no CRS."
            )

        if raster_crs is None:
            raise ValueError(
                "ERROR: Raster has no CRS."
            )

        if tile_gdf.crs != raster_crs:

            print(
                "Reprojecting annotations "
                "to raster CRS..."
            )

            tile_gdf = tile_gdf.to_crs(
                raster_crs
            )


        yolo_lines = []


        # ----------------------------------------------------
        # Process polygons
        # ----------------------------------------------------

        for geometry in tile_gdf.geometry:

            if geometry is None:
                continue

            if geometry.is_empty:
                continue


            # ------------------------------------------------
            # Polygon
            # ------------------------------------------------

            if isinstance(
                geometry,
                Polygon
            ):

                line = polygon_to_yolo(
                    geometry,
                    transform,
                    width,
                    height
                )

                if line:
                    yolo_lines.append(line)
                else:
                    skipped_polygons += 1


            # ------------------------------------------------
            # MultiPolygon
            # ------------------------------------------------

            elif isinstance(
                geometry,
                MultiPolygon
            ):

                for polygon in geometry.geoms:

                    line = polygon_to_yolo(
                        polygon,
                        transform,
                        width,
                        height
                    )

                    if line:
                        yolo_lines.append(line)
                    else:
                        skipped_polygons += 1


        # ----------------------------------------------------
        # Train / Validation
        # ----------------------------------------------------

        if tile_id in train_tiles:

            image_output = os.path.join(
                TRAIN_IMAGES,
                tile_id + ".tif"
            )

            label_output = os.path.join(
                TRAIN_LABELS,
                tile_id + ".txt"
            )

        else:

            image_output = os.path.join(
                VAL_IMAGES,
                tile_id + ".tif"
            )

            label_output = os.path.join(
                VAL_LABELS,
                tile_id + ".txt"
            )


        # ----------------------------------------------------
        # Copy image
        # ----------------------------------------------------

        shutil.copy2(
            tif_path,
            image_output
        )


        # ----------------------------------------------------
        # Save YOLO labels
        # ----------------------------------------------------

        with open(
            label_output,
            "w"
        ) as f:

            f.write(
                "\n".join(yolo_lines)
            )

            if yolo_lines:
                f.write("\n")


        total_polygons += len(
            yolo_lines
        )


        print(
            f"Polygons converted: "
            f"{len(yolo_lines)}"
        )


# ============================================================
# CREATE DATA.YAML
# ============================================================

yaml_path = os.path.join(
    OUTPUT_FOLDER,
    "data.yaml"
)

yaml_content = """path: .

train: images/train
val: images/val

names:
  0: tree
"""


with open(
    yaml_path,
    "w"
) as f:

    f.write(yaml_content)


# ============================================================
# FINAL REPORT
# ============================================================

print()
print("===================================")
print("CONVERSION COMPLETED")
print("===================================")

print(
    f"Total YOLO polygons: "
    f"{total_polygons}"
)

print(
    f"Skipped polygons: "
    f"{skipped_polygons}"
)

print()
print("Dataset:")
print(OUTPUT_FOLDER)

print()
print("data.yaml:")
print(yaml_path)

print()
print("===================================")
