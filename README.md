# 🌳 UAV Tree Center Extraction

> Automated tree crown detection and GIS-ready tree center point extraction from UAV orthomosaics using YOLO11n-seg, Python, and QGIS.

<p align="center">
  <img src="docs/images/before-after.png" width="90%">
</p>

---

## 🎯 Project Overview

This project presents an automated GIS and Deep Learning workflow for detecting tree crowns from UAV orthomosaics and generating corresponding tree center points for GIS mapping.

The workflow combines:

- UAV photogrammetry
- Orthomosaic processing
- QGIS-based annotation
- YOLO11n-seg
- Python automation
- Tree crown segmentation
- Centroid extraction
- Geospatial processing
- GeoPackage generation

The main objective is to reduce repetitive manual tree point digitization and produce a GIS-ready tree inventory from high-resolution UAV imagery.

---

## 🔄 Before → After

### Before

UAV orthomosaic containing tree crowns without automatically generated tree center points.

### After

Automatically detected tree crowns are converted into GIS point features representing the estimated center of each detected tree crown.

The result can be directly visualized and further analyzed in QGIS.

---

## ⚙️ Workflow

```text
UAV Orthomosaic
       ↓
Orthomosaic Tiling
       ↓
QGIS Tree Crown Annotation
       ↓
QGIS → YOLO Segmentation Labels
       ↓
YOLO11n-seg Model Training
       ↓
Full-Area Tree Detection
       ↓
Tree Crown Segmentation
       ↓
Centroid Extraction
       ↓
Duplicate Detection Removal
       ↓
GeoPackage Generation
       ↓
QGIS Visualization


---

## ✨ Key Features

- UAV orthomosaic tiling with overlap
- Preservation of GeoTIFF CRS and spatial transform
- QGIS-based tree crown annotation
- Conversion of QGIS polygons to YOLO segmentation labels
- YOLO11n-seg based tree crown detection
- Full-area tiled inference
- Tree crown centroid extraction
- Duplicate detection removal
- GeoPackage output
- QGIS-ready GIS data
- Python-based automation

---

## 📁 Project Structure

```text
uav-tree-center-extraction/
│
├── docs/
│   └── images/
│       └── before-after.png
│
├── scripts/
│   ├── tile_orthomosaic.py
│   ├── qgis_to_yolo.py
│   └── full_tree_detection.py
│
├── .gitignore
├── README.md
└── requirements.txt

## 🛠️ Technologies
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


🚀 Installation
1. Clone the repository
git clone https://github.com/GeoPythonwithBapan/uav-tree-center-extraction.git
cd uav-tree-center-extraction
2. Create a Python virtual environment
python -m venv venv

Activate the environment according to your operating system.

3. Install dependencies
pip install -r requirements.txt

Note: PyTorch installation may differ depending on whether the system uses CPU or NVIDIA GPU/CUDA. Install the appropriate PyTorch version separately for your environment.

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

tile_id
class
geometry

The tree class is represented as:

0 = tree
Step 3 — Convert QGIS Annotations to YOLO Format

Run:

python scripts/qgis_to_yolo.py

This converts the QGIS polygon annotations into YOLO segmentation label format and prepares the dataset for model training.

The script also creates a training and validation split based on tiles.

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
🗺️ GIS Output

The generated points retain the coordinate reference system of the input orthomosaic.

This allows the detected tree points to be overlaid directly on the original UAV orthomosaic in QGIS.

⚠️ Important Note

The generated point represents the centroid of the detected tree crown.

It should therefore be considered an estimated tree center rather than a guaranteed exact trunk location.

The result can be affected by:

Tree crown shape
Dense vegetation
Overlapping crowns
Image quality
UAV viewing geometry
Detection confidence
Training dataset quality

Proper validation is recommended before using the output for high-precision applications.

🔮 Future Improvements

Possible future developments include:

Improved duplicate detection using mask IoU and spatial distance
Better handling of overlapping tree crowns
Species-level tree classification
Improved performance in dense plantations
Automated model evaluation reports
QGIS plugin integration
Batch processing of multiple orthomosaics
Automated quality-control tools
GUI-based processing workflow
👤 Author

Bapan Dutta

GIS Executive | Remote Sensing & GIS | UAV Mapping | GeoAI

This project combines GIS, UAV photogrammetry, computer vision, and Deep Learning for automated geospatial feature extraction.

