#!/bin/bash +x

VECTOR_COLOR="docker run --rm -v ${PWD}:/mnt developmentseed/vector_color:v1"
GEOKIT_NODE="docker run --rm -v ${PWD}:/mnt/data/ developmentseed/geokit:node.latest"

BOUNDARY=$1
FOLDER=${BOUNDARY%.*}
TILES_FILE=${FOLDER}_tiles.geojson

$GEOKIT_NODE geokit tilecover ${BOUNDARY} --zoom=20 >${TILES_FILE}
# rm ${FOLDER}/*_output.png
# rm ${FOLDER}/*.geojson

$VECTOR_COLOR python src/range.py \
    --geojson_tiles_file=${TILES_FILE} \
    --output_folder=${FOLDER} \
    --url_map_service="https://tiles.lulc.ds.io/mosaic/naip.latest/tiles/{z}/{x}/{y}?bidx=1,2,3" \
    --hue=20,75 \
    --value=3,145 \
    --saturation=15,191 \
    --area=200,100000 \
    --kernel=3 \
    --tags=class=tree_canopy \
    --tags=project=LULC_labeling \
    --tags=aoi=detroit \
    --geojson_output="${FOLDER}.geojson"

# # python src/obj_recognizion.py  \
# # --img_file=data/tiles_20/282364-387528-20.png \
# # --hue=66,75 \
# # --value=55,145 \
# # --saturation=50,191
