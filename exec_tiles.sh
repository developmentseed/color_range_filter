#!/bin/bash +x

VECTOR_COLOR="docker run --rm -v ${PWD}:/mnt developmentseed/vector_color:v1"
GEOKIT_NODE="docker run --rm -v ${PWD}:/mnt/data/ developmentseed/geokit:node.latest"

BOUNDARY=$1
FOLDER=${BOUNDARY%.*}
TILES_FILE=${FOLDER}_tiles.geojson

################################################################
######## check the right ranges to run the script
################################################################
# python src/hsv_color_picker.py --image_file=data/tile/tile.png

################################################################
######## Get Tree Canopy from supertiles
################################################################
rm ${FOLDER}/*.geojson
$GEOKIT_NODE geokit tilecover ${BOUNDARY} --zoom=20 >${TILES_FILE}
${VECTOR_COLOR} python src/range.py \
    --geojson_tiles_file=${TILES_FILE} \
    --output_folder=${FOLDER} \
    --url_map_service="https://tiles.lulc.ds.io/mosaic/naip.latest/tiles/{z}/{x}/{y}?bidx=1,2,3" \
    --hsv_lower=20,3,15 \
    --hsv_upper=75,145,191 \
    --area=2000,100000 \
    --kernel=2 \
    --tags=class=tree_canopy \
    --tags=project=LULC_labeling \
    --tags=aoi=detroit \
    --geojson_output=${FOLDER}_tree.geojson

zip ${FOLDER}.zip ${FOLDER}/*.geojson
