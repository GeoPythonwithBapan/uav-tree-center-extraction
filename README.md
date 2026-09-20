# 🌳 UAV Tree Center Extraction

> Automated tree crown detection and GIS-ready tree center point extraction from UAV orthomosaics using YOLO11n-seg, Python, and QGIS.

<p align="center">
  <img src="docs/images/before-after.png" width="90%">
</p>

---

## 🎯 Project Overview

This project presents an automated GIS and Deep Learning workflow for detecting tree crowns from UAV orthomosaics and generating corresponding tree center points for GIS mapping.

The workflow combines UAV photogrammetry, computer vision, deep learning, and GIS automation to reduce repetitive manual tree point digitization.

The main objective is to generate GIS-ready tree center points from high-resolution UAV imagery.

---

## 🔄 Before → After

### Before

UAV orthomosaic containing tree crowns without automatically generated tree center points.

### After

Automatically detected tree crowns are converted into GIS point features representing the estimated center of each detected tree crown.

The final result can be visualized and further analyzed in QGIS.

---

## ⚙️ Workflow


UAV Orthomosaic
       -
Orthomosaic Tiling
       -
QGIS Tree Crown Annotation
       -
QGIS → YOLO Segmentation Labels
       -
YOLO11n-seg Model Training
       -
Full-Area Tree Detection
       -
Tree Crown Segmentation
       -
Centroid Extraction
       -
Duplicate Detection Removal
       -
GeoPackage Generation
       -
QGIS Visualization

---
✨ Key Features

UAV orthomosaic tiling with overlap

Preservation of GeoTIFF CRS and spatial transform

QGIS-based tree crown annotation

Conversion of QGIS polygons to YOLO segmentation labels

YOLO11n-seg based tree crown detection

Full-area tiled inference

Tree crown centroid extraction

Duplicate detection removal

GeoPackage output

QGIS-ready GIS data

Python-based automation

---
🛠️ Technologies
| Technology  | Purpose                          |
| ----------- | -------------------------------- |
| Python      | Workflow automation              |
| QGIS        | Annotation and GIS visualization |
| YOLO11n-seg | Tree crown segmentation          |
| Rasterio    | Raster processing                |
| GeoPandas   | Geospatial vector processing     |
| Shapely     | Geometry operations              |
| NumPy       | Numerical processing             |
| GeoPackage  | GIS output format                |

---
📌 Workflow Setup

Step 1 — Orthomosaic Tiling

Use:
scripts/tile_orthomosaic.py

This script divides a large UAV orthomosaic into smaller tiles suitable for annotation and Deep Learning processing.

Default settings:

Tile size: 1024 × 1024
Overlap: 512 pixels

The generated tiles retain their spatial reference information.

Step 2 — Tree Crown Annotation

Open the generated tiles in QGIS and create polygon annotations around visible tree crowns.

The annotation layer should contain:

tile_id,
class,
geometry

The tree class is represented as:

0 = tree

Step 3 — Convert QGIS Annotations to YOLO Format

Run:

python scripts/qgis_to_yolo.py

This converts the QGIS polygon annotations into YOLO segmentation label format and prepares the dataset for model training.

The script also creates a training and validation split based on tiles.

---
🧠 YOLO11n-seg Model Training

After preparing the dataset, train the YOLO segmentation model using Ultralytics.

Example:

yolo train model=yolo11n-seg.pt data="path/to/data.yaml" epochs=100 imgsz=1024

Training parameters can be adjusted according to:

Dataset size
GPU memory
Image resolution
Number of epochs
Batch size
---
🔍 Full-Area Tree Detection

After training, use:

scripts/full_tree_detection.py

The script performs tiled inference over the complete UAV orthomosaic.

The processing workflow is:

Large Orthomosaic
       ↓
Image Tiling
       ↓
YOLO11n-seg Prediction
       ↓
Tree Crown Masks
       ↓
Polygon Generation
       ↓
Centroid Extraction
       ↓
Coordinate Transformation
       ↓
Duplicate Removal
       ↓
GeoPackage

---

📤 Output

The final output is a GIS-ready GeoPackage (.gpkg) containing tree center points.

Example:

tree_centroids.gpkg

The output can be loaded directly into QGIS for:

Tree inventory mapping
Tree counting
Spatial analysis
Distance analysis
Plantation monitoring
Asset mapping
Further GIS analysis

---
🗺️ GIS Output

The generated points retain the coordinate reference system of the input orthomosaic.

This allows the detected tree points to be overlaid directly on the original UAV orthomosaic in QGIS.

The output can be further used for spatial analysis, visualization, and tree inventory mapping.

---

👤 Author

Bapan Dutta

GIS Executive | Remote Sensing & GIS | UAV Mapping | GeoAI

This project combines GIS, UAV photogrammetry, computer vision, and Deep Learning for automated geospatial feature extraction.

