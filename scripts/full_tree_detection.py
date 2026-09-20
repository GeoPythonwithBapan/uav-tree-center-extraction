import os
import rasterio
import geopandas as gpd

from rasterio.windows import Window
from rasterio.transform import xy
from shapely.geometry import Point, Polygon
from ultralytics import YOLO


# =========================================================
# USER SETTINGS
# =========================================================

# Trained YOLO segmentation model
MODEL_PATH = r"YOUR_MODEL_PATH/best.pt"

# Input UAV orthomosaic
INPUT_RASTER = r"YOUR_INPUT_ORTHOMOSAIC.tif"

# Output GeoPackage
OUTPUT_GPKG = r"YOUR_OUTPUT_FOLDER/tree_centroids.gpkg"


# =========================================================
# DETECTION SETTINGS
# =========================================================

TILE_SIZE = 1024

# Overlap between neighbouring tiles
OVERLAP = 512

# YOLO confidence threshold
CONFIDENCE = 0.10

# GPU device
# Use 0 for NVIDIA GPU
# Use "cpu" for CPU
DEVICE = 0

# Minimum distance between detected tree centroids
# Used for duplicate removal
DUPLICATE_DISTANCE = 6.0


# =========================================================
# CREATE OUTPUT DIRECTORY
# =========================================================

output_folder = os.path.dirname(OUTPUT_GPKG)

if output_folder:
    os.makedirs(
        output_folder,
        exist_ok=True
    )


# =========================================================
# LOAD YOLO MODEL
# =========================================================

print()
print("====================================")
print("LOADING YOLO MODEL")
print("====================================")

model = YOLO(MODEL_PATH)

print("Model loaded successfully.")


# =========================================================
# OPEN ORTHOMOSAIC
# =========================================================

with rasterio.open(INPUT_RASTER) as src:

    width = src.width
    height = src.height
    crs = src.crs

    print()
    print("====================================")
    print("INPUT ORTHOMOSAIC")
    print("====================================")

    print("Width :", width)
    print("Height:", height)
    print("Bands :", src.count)
    print("CRS   :", crs)


    if crs is None:
        raise ValueError(
            "ERROR: Input raster has no CRS."
        )


    # =====================================================
    # TILE STEP
    # =====================================================

    STEP = TILE_SIZE - OVERLAP

    if STEP <= 0:
        raise ValueError(
            "ERROR: OVERLAP must be smaller than TILE_SIZE."
        )

    print()
    print("Tile size :", TILE_SIZE)
    print("Overlap   :", OVERLAP)
    print("Step      :", STEP)


    # =====================================================
    # STORE DETECTIONS
    # =====================================================

    detections = []

    tile_counter = 0


    # =====================================================
    # SLIDING WINDOW
    # =====================================================

    for y in range(
        0,
        height,
        STEP
    ):

        for x in range(
            0,
            width,
            STEP
        ):

            tile_counter += 1


            # -------------------------------------------------
            # Window dimensions
            # -------------------------------------------------

            win_width = min(
                TILE_SIZE,
                width - x
            )

            win_height = min(
                TILE_SIZE,
                height - y
            )


            window = Window(
                col_off=x,
                row_off=y,
                width=win_width,
                height=win_height
            )


            # -------------------------------------------------
            # Read RGB bands
            # -------------------------------------------------

            if src.count < 3:

                raise ValueError(
                    "ERROR: Raster must contain at least 3 bands."
                )


            image = src.read(
                [1, 2, 3],
                window=window
            )


            # CHW -> HWC
            image = image.transpose(
                1,
                2,
                0
            )


            print(
                f"\nTile {tile_counter}: "
                f"x={x}, y={y}, "
                f"size={win_width}x{win_height}"
            )


            # -------------------------------------------------
            # YOLO prediction
            # -------------------------------------------------

            results = model.predict(
                source=image,
                imgsz=TILE_SIZE,
                conf=CONFIDENCE,
                device=DEVICE,
                verbose=False
            )


            result = results[0]


            # -------------------------------------------------
            # Check segmentation masks
            # -------------------------------------------------

            if result.masks is None:

                print(
                    "  No trees detected."
                )

                continue


            masks = result.masks.xy
            boxes = result.boxes


            print(
                f"  Trees detected: "
                f"{len(masks)}"
            )


            # -------------------------------------------------
            # Process each detected tree
            # -------------------------------------------------

            for i, polygon in enumerate(masks):

                if polygon is None:
                    continue

                if len(polygon) < 3:
                    continue


                # ---------------------------------------------
                # Create polygon
                # ---------------------------------------------

                polygon_points = [
                    (
                        float(px),
                        float(py)
                    )
                    for px, py in polygon
                ]


                poly = Polygon(
                    polygon_points
                )


                if not poly.is_valid:

                    poly = poly.buffer(0)


                if poly.is_empty:
                    continue


                # ---------------------------------------------
                # Crown centroid
                # ---------------------------------------------

                centroid = poly.centroid


                tile_px = centroid.x
                tile_py = centroid.y


                # ---------------------------------------------
                # Tile pixel -> global raster pixel
                # ---------------------------------------------

                global_px = x + tile_px
                global_py = y + tile_py


                # ---------------------------------------------
                # Pixel -> map coordinates
                # ---------------------------------------------

                map_x, map_y = xy(
                    src.transform,
                    global_py,
                    global_px
                )


                # ---------------------------------------------
                # Confidence
                # ---------------------------------------------

                confidence = float(
                    boxes.conf[i].item()
                )


                detections.append({
                    "x": map_x,
                    "y": map_y,
                    "confidence": confidence
                })


# =========================================================
# REMOVE DUPLICATE DETECTIONS
# =========================================================

print()
print("====================================")
print("DUPLICATE REMOVAL")
print("====================================")

print(
    "Raw detections:",
    len(detections)
)


# Highest-confidence detections first
detections.sort(
    key=lambda d: d["confidence"],
    reverse=True
)


final_detections = []


for detection in detections:

    point = Point(
        detection["x"],
        detection["y"]
    )


    duplicate = False


    for existing in final_detections:

        existing_point = Point(
            existing["x"],
            existing["y"]
        )


        distance = point.distance(
            existing_point
        )


        if distance < DUPLICATE_DISTANCE:

            duplicate = True
            break


    if not duplicate:

        final_detections.append(
            detection
        )


print(
    "Final detections:",
    len(final_detections)
)


# =========================================================
# CREATE GEODATAFRAME
# =========================================================

records = []


for i, detection in enumerate(
    final_detections,
    start=1
):

    records.append({

        "tree_id": i,

        "confidence": round(
            detection["confidence"],
            6
        ),

        "geometry": Point(
            detection["x"],
            detection["y"]
        )
    })


gdf = gpd.GeoDataFrame(
    records,
    geometry="geometry",
    crs=crs
)


# =========================================================
# SAVE GEOPACKAGE
# =========================================================

if os.path.exists(
    OUTPUT_GPKG
):

    os.remove(
        OUTPUT_GPKG
    )


gdf.to_file(
    OUTPUT_GPKG,
    layer="tree_centroids",
    driver="GPKG"
)


# =========================================================
# FINAL SUMMARY
# =========================================================

print()
print("====================================")
print("FULL TREE DETECTION COMPLETED")
print("====================================")

print(
    "Final trees:",
    len(gdf)
)

print(
    "CRS:",
    gdf.crs
)

print(
    "Output:",
    OUTPUT_GPKG
)

print()
print("First 10 detections:")

print(
    gdf.head(10)
)

print()
print("====================================")
