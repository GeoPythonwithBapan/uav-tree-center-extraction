import os
import rasterio
from rasterio.windows import Window
from rasterio.windows import transform as window_transform


# ============================================================
# USER SETTINGS
# ============================================================

# Change these paths according to your project
INPUT_ORTHO = r"YOUR_INPUT_ORTHOMOSAIC.tif"

OUTPUT_FOLDER = r"YOUR_OUTPUT_FOLDER"

TILE_SIZE = 1024
OVERLAP = 512


# ============================================================
# CREATE OUTPUT FOLDER
# ============================================================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ============================================================
# OPEN GEOTIFF
# ============================================================

with rasterio.open(INPUT_ORTHO) as src:

    print("===================================")
    print("ORTHOMOSAIC INFORMATION")
    print("===================================")

    print(f"Width     : {src.width}")
    print(f"Height    : {src.height}")
    print(f"Bands     : {src.count}")
    print(f"CRS       : {src.crs}")
    print(f"Transform : {src.transform}")
    print()

    # Check CRS
    if src.crs is None:
        raise ValueError(
            "ERROR: Input GeoTIFF has no CRS!"
        )

    width = src.width
    height = src.height

    step = TILE_SIZE - OVERLAP

    tile_number = 0


    # ========================================================
    # CREATE TILES
    # ========================================================

    for y in range(0, height, step):

        for x in range(0, width, step):

            # -----------------------------------------------
            # Tile dimensions
            # -----------------------------------------------

            tile_width = min(
                TILE_SIZE,
                width - x
            )

            tile_height = min(
                TILE_SIZE,
                height - y
            )


            window = Window(
                x,
                y,
                tile_width,
                tile_height
            )


            # -----------------------------------------------
            # Read image
            # -----------------------------------------------

            image = src.read(
                window=window
            )


            # -----------------------------------------------
            # Tile transform
            # -----------------------------------------------

            tile_transform = window_transform(
                window,
                src.transform
            )


            # -----------------------------------------------
            # Tile filename
            # -----------------------------------------------

            tile_number += 1

            filename = f"tile_{tile_number:05d}.tif"

            output_path = os.path.join(
                OUTPUT_FOLDER,
                filename
            )


            # -----------------------------------------------
            # Create tile metadata
            # -----------------------------------------------

            profile = src.profile.copy()

            profile.update({

                "driver": "GTiff",

                "height": tile_height,

                "width": tile_width,

                "transform": tile_transform,

                "crs": src.crs,

                "compress": "LZW"

            })


            # -----------------------------------------------
            # Write GeoTIFF tile
            # -----------------------------------------------

            with rasterio.open(
                output_path,
                "w",
                **profile
            ) as dst:

                dst.write(image)


            print(
                f"Created: {filename}"
            )


# ============================================================
# COMPLETED
# ============================================================

print()
print("===================================")
print("TILING COMPLETED")
print("===================================")

print(f"Total tiles : {tile_number}")

print()
print("Output folder:")
print(OUTPUT_FOLDER)

print()
print("Each tile retains:")
print("✓ CRS")
print("✓ Geographic transform")
print("✓ Correct geographic position")

print("===================================")
