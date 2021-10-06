#!/bin/bash +x

VECTOR_COLOR="docker run --rm -v ${PWD}:/mnt developmentseed/vector_color:v1"
GEOKIT_NODE="docker run --rm -v ${PWD}:/mnt/data/ developmentseed/geokit:node.latest"
BOUNDARY=$1
FOLDER=${BOUNDARY%.*}
TILES_FILE=${FOLDER}_tiles.geojson

$GEOKIT_NODE geokit tilecover ${BOUNDARY} --zoom=20 >${TILES_FILE}
# rm ${FOLDER}/*_output.png
# rm ${FOLDER}/*.geojson

# Tree Canopy
# $VECTOR_COLOR python src/range.py \
#     --geojson_tiles_file=${TILES_FILE} \
#     --output_folder=${FOLDER} \
#     --url_map_service="https://tiles.lulc.ds.io/mosaic/naip.latest/tiles/{z}/{x}/{y}?bidx=1,2,3" \
#     --hue=20,75 \
#     --value=3,145 \
#     --saturation=15,191 \
#     --area=2000,100000 \
#     --kernel=3 \
#     --tags=class=tree_canopy \
#     --tags=project=LULC_labeling \
#     --tags=aoi=detroit \
#     --geojson_output="${FOLDER}_detection.geojson"

# Water
$VECTOR_COLOR python src/range.py \
    --geojson_tiles_file=${TILES_FILE} \
    --output_folder=${FOLDER} \
    --url_map_service="https://tiles.lulc.ds.io/mosaic/naip.latest/tiles/{z}/{x}/{y}?bidx=1,2,3" \
    --hue=89,109 \
    --saturation=151,231 \
    --value=87,107 \
    --area=100,5000 \
    --kernel=2 \
    --tags=class=water \
    --tags=project=LULC_labeling \
    --tags=aoi=detroit \
    --geojson_output="${FOLDER}_water.geojson"

# --hue=0,48 \
# --value=52,169 \
# --saturation=147,247 \


wget https://tiles.lulc.ds.io/mosaic/naip.latest/tiles/20/282031/388328?bidx=1,2,3 -O data/water.png
python src/pick_hvs.py --image_file=data/water.png

python src/hsv_color_picker.py --image_file=data/water.png

python src/obj_recognizion.py \
    --img_file=data/20-282016-388308.png \
    --hue=89,109 \
    --saturation=81,101 \
    --value=165,245

#  python src/clip.py \
#     --geojson_data=data/ediyes_lulc_detection.geojson \
#     --geojson_poly=data/ediyes_lulc.geojson \
#     --geojson_output=data/ediyes_lulc_detection_clipped.geojson
