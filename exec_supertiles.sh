#!/bin/bash +x

VECTOR_COLOR="docker run --rm -v ${PWD}:/mnt developmentseed/vector_color:v1"
SUPER_TILES="docker run -v ${PWD}:/mnt devseed/super-tiles:v1 "
# ./exec_supertiles.sh data/box_162
SUPERTILES_FOLDER=$1
BOUNDARY=$2

################################################################
######## Create supertiles for boundary
################################################################
# $GEOKIT_NODE geokit tilecover ${BOUNDARY} --zoom=16 >${TILES_FILE}
# $SUPER_TILES \
#     super_tiles \
#     --geojson_file=${TILES_FILE}\
#     --zoom=20 \
#     --bounds_multiplier=14 \
#     --url_map_service="https://tiles.lulc.ds.io/mosaic/naip.latest/tiles/{z}/{x}/{y}?bidx=1,2,3" \
#     --url_map_service_type="tms" \
#     --tiles_folder=${FOLDER}/tiles \
#     --st_tiles_folder=${FOLDER}/super_tiles \
#     --geojson_output=${FOLDER}/schools.geojson \
#     --geojson_output_coverage=${FOLDER}/schools_supertiles_coverage.geojson

################################################################
######## check the right ranges to run the script
################################################################
# python src/hsv_color_picker.py --image_file=data/box_27/281856-388368-20-st.png

###############################################################
####### Get grass from supertiles
###############################################################
rm ${SUPERTILES_FOLDER}/*.geojson
${VECTOR_COLOR} python src/range.py \
    --supertile=True \
    --supertile_size=4096 \
    --supertile_folder=${SUPERTILES_FOLDER} \
    --hsv_lower=75,27,85 \
    --hsv_upper=99,51,189 \
    --area=2500,8000 \
    --kernel=1 \
    --tags=class=grass_shrub \
    --tags=project=LULC_labeling \
    --tags=aoi=detroit \
    --geojson_output=${SUPERTILES_FOLDER}_grass.geojson
zip ${SUPERTILES_FOLDER}.zip ${SUPERTILES_FOLDER}/*.geojson
