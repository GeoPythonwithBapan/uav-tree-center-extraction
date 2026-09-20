# UAV Tree Center Extraction

Automated tree center point extraction from UAV orthomosaics using YOLO11n-seg, Python, and QGIS.

## Overview

This project provides a GIS and Deep Learning workflow for automatically detecting tree crowns from UAV orthomosaics and generating tree center points for GIS mapping.

The workflow combines UAV photogrammetry, computer vision, deep learning, and GIS automation to reduce repetitive manual tree digitization.

## Workflow

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
Duplicate Removal
       ↓
GeoPackage Output
       ↓
QGIS Visualization
