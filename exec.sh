#!/bin/bash +x

VECTOR_COLOR="docker run --rm -v ${PWD}:/mnt developmentseed/vector_color:v1"
GEOKIT_NODE="docker run --rm -v ${PWD}:/mnt/data/ developmentseed/geokit:node.latest"
GEOKIT_PYTHON="docker run --rm -v ${PWD}:/mnt/data developmentseed/geokit:python.update_geo_py_scripts"

BOUNDARY=$1
FOLDER=${BOUNDARY%.*}
TILES_FILE=${FOLDER}_tiles.geojson
$GEOKIT_NODE geokit tilecover ${BOUNDARY} --zoom=20 >${TILES_FILE}

# # Tree Canopy
# ${VECTOR_COLOR} python src/range.py \
#     --geojson_tiles_file=${TILES_FILE} \
#     --output_folder=${FOLDER} \
#     --url_map_service="https://tiles.lulc.ds.io/mosaic/naip.latest/tiles/{z}/{x}/{y}?bidx=1,2,3" \
#     --hsv_lower=20,3,15 \
#     --hsv_upper=75,145,191 \
#     --area=2000,100000 \
#     --kernel=2 \
#     --tags=class=tree_canopy \
#     --tags=project=LULC_labeling \
#     --tags=aoi=detroit \
#     --geojson_output=${FOLDER}_tree.geojson

# ${GEOKIT_PYTHON} geo clip \
# --geojson_input  ${FOLDER}_tree.geojson \
# --geojson_boundary ${BOUNDARY} \
# --geojson_output ${FOLDER}_tree_clip.geojson

# Water
$VECTOR_COLOR python src/range.py \
    --geojson_tiles_file=${TILES_FILE} \
    --output_folder=${FOLDER} \
    --url_map_service="https://tiles.lulc.ds.io/mosaic/naip.latest/tiles/{z}/{x}/{y}?bidx=1,2,3" \
    --hsv_lower=13,62,189 \
    --hsv_upper=57,101,251 \
    --area=100,150000 \
    --kernel=3 \
    --tags=class=water \
    --tags=project=LULC_labeling \
    --tags=aoi=detroit \
    --geojson_output="${FOLDER}_water.geojson"

# --hsv_lower=4,85,141 \
# --hsv_upper=59,214,241 \
# python src/hsv_color_picker.py --image_file=data/water_2.png

# python src/obj_recognizion.py \
#     --image_file=data/water_2.png \
#     --hsv_lower=7,73,145 \
#     --hsv_upper=35,101,253 \
#     --kernel=3
