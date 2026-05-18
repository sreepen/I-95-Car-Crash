# U.S. Traffic Accident Severity Analysis — Big Data Analytics
 
A large-scale geospatial and predictive analysis of 7.7 million U.S. traffic accidents using PySpark on Penn State's ICDS Roar supercomputer, combining heatmap visualization, Sankey flow diagrams, and Random Forest classification to identify the key drivers of accident severity.
 
## Overview
 
Traffic accident analytics informs safer road design, emergency resource allocation, and public safety policy. This project applies big data techniques to a 3.06 GB national accident dataset, answering two core questions: **where do accidents cluster geographically**, and **what factors drive severe outcomes**.
 
The scale of the data — millions of records with 46 features spanning weather, road infrastructure, and geospatial coordinates — makes this infeasible with conventional single-machine tools. All major processing was performed using PySpark RDD operations on a distributed 4-node HPC cluster.
 
**Course:** DS/CMPSC 410 — Big Data Analytics, Penn State University (Fall 2025)  
**Team:** Katherine Thornber, Zachary Smith, Mitchell Darling, Sree Penumuchu, Anant Mishra, Vuk Radulovic  
**Cluster:** Penn State ICDS Roar (4 nodes, 64 GB memory)  
**Data:** [US Accidents (Kaggle) — Sobhan Moosavi](https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents)
 
---
 
## Key Findings
 
### Random Forest — Top Severity Predictors
| Feature | Importance Score |
|---------|-----------------|
| Wind Speed (mph) | 0.316 |
| Traffic Signal | 0.196 |
| Temperature (°F) | 0.145 |
| Hour (time of day) | 0.101 |
| Visibility (mi) | 0.068 |
| Precipitation (in) | 0.053 |
 
- **Wind speed is the dominant predictor** of accident severity — high winds are a primary contributor to more severe outcomes
- **Traffic signal presence** is the second strongest predictor — road control infrastructure plays a critical role in determining severity
- Assumed risks like precipitation, rush hour flags, and freezing temperatures had relatively low importance, suggesting they affect *frequency* more than *severity*
### Geospatial Findings
- Accidents are concentrated along **U.S. Interstate Highway corridors** and in **major metropolitan areas**
- Pennsylvania heatmaps reveal dense clusters in **Philadelphia, Pittsburgh**, and directly on the **Penn State campus** (I-99 / US-322)
- Sankey flow diagrams confirm that highways are not just high-frequency accident locations — accident paths *trace the highway network itself*, showing continuous linear risk rather than isolated hotspots
---
 
## Methods
 
### Pipeline
1. **Data Ingestion** — PySpark reads the full 3.06 GB CSV into distributed RDDs
2. **Preprocessing** — Missing value imputation, categorical standardization (grouping similar weather descriptions), feature engineering (time-of-day bins, season flags, rush hour indicators)
3. **Geospatial Aggregation** — Accident density computed by lat/lon grid for heatmap generation
4. **Predictive Modeling** — Random Forest classifier trained on severity as the target variable
5. **Visualization** — Folium heatmaps + GeoPandas/Geoplot Sankey diagrams
### Random Forest (Sree Penumuchu)
- Built in scikit-learn on a representative sample for local prototyping
- Features: temperature, visibility, wind speed, precipitation, hour, rush hour flag, infrastructure booleans (junction, stop, traffic signal), low visibility flag, freezing temp flag
- Target: binary high severity (severity ≥ 3)
- 100 estimators, max depth 10, parallelized with `n_jobs=-1`
- Feature importance ranked and visualized as a color-scaled horizontal bar chart
### Heatmaps (Sree Penumuchu)
- Built with Folium + HeatMap plugin
- Parameterized pipeline generating 10 filtered maps across state × severity combinations
- Auto-fit bounds, configurable radius/blur, saved as standalone HTML files
### Sankey Diagrams (Katherine Thornber)
- Origin-destination flow lines built from accident start/end coordinates using GeoPandas LineString
- Custom Albers Equal Area projection fitted per state for accurate spatial rendering
- Severity-colored flows overlaid on TIGER/Line state boundary shapefiles
---
 
## Scalability Results
 
| Task | Nodes | Memory | Notes |
|------|-------|--------|-------|
| Heatmap generation | 2 | 64 GB | Ran in several minutes; well-distributed |
| Sankey visualization | 4 | 64 GB | Most demanding task; required batch decomposition |
| Random Forest training | 4 | 64 GB | Distributed across full dataset |
 
---
 
## Repository Structure
 
```
├── DS410_predictive_modeling.ipynb   # Random Forest model + feature importance visualization
├── heat_map.py                       # Folium heatmap pipeline (parameterized by state/severity)
├── sankey.py                         # PySpark + GeoPandas Sankey flow diagram generator
└── Team_I-95_DS410_Project_Report.pdf  # Full project report
```
 
---
 
## Setup
 
```bash
pip install pyspark pandas numpy scikit-learn matplotlib folium
pip install geopandas geoplot cartopy shapely
```
 
> **Data:** The full dataset (3.06 GB) is too large for this repository. Download from [Kaggle](https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents) and update the file path in each script.
 
> **Cluster scripts** (`heat_map.py`, `sankey.py`) are configured for Penn State's ICDS Roar storage paths (`/storage/work/...`). Update paths for local execution.
 
---
 
## Individual Contributions
 
- **Sree Penumuchu** — Random Forest model, feature engineering, feature importance visualization, Folium heatmap pipeline, formal analysis and results writing
- **Katherine Thornber** — Sankey diagram pipeline, methodology, formal analysis
- **Mitchell Darling** — Data curation, preprocessing pipeline, visualization, formal analysis
- **Zachary Smith** — PySpark pipeline architecture, methodology
- **Anant Mishra & Vuk Radulovic** — Data resources, investigation
