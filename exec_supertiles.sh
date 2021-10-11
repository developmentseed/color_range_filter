#!/bin/bash +x

VECTOR_COLOR="docker run --rm -v ${PWD}:/mnt developmentseed/vector_color:v1"
GEOKIT_NODE="docker run --rm -v ${PWD}:/mnt/data/ developmentseed/geokit:node.latest"
GEOKIT_PYTHON="docker run --rm -v ${PWD}:/mnt/data developmentseed/geokit:python.update_geo_py_scripts"
SUPER_TILES="docker run -v ${PWD}:/mnt devseed/super-tiles:v1 "
GDAL="docker run -v ${PWD}:/var/task lambgeo/lambda-gdal:3.3-al2"

BOUNDARY=$1
FOLDER=${BOUNDARY%.*}
TILES_FILE=${FOLDER}_tiles.geojson

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
# python src/hsv_color_picker.py --image_file=data/area/super_tiles/281856-388368-20-st.png

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

# ${VECTOR_COLOR} python src/range.py \
#     --supertile=True \
#     --supertile_size=4096 \
#     --supertile_folder=data/area/super_tiles/ \
#     --output_folder=data/area/color_detect \
#     --hsv_lower=28,21,20 \
#     --hsv_upper=126,119,198 \
#     --area=9900,9900000 \
#     --kernel=9 \
#     --tags=class=tree_canopy \
#     --tags=project=LULC_labeling \
#     --tags=aoi=detroit \
#     --geojson_output=data/area_tree.geojson

# zip data/area_tree.zip data/area/super_tiles/*.geojson

# # # Get Tree Canopy from supertiles
# rm data/area/super_tiles/*.geojson
# ${VECTOR_COLOR} python src/range.py \
#     --supertile=True \
#     --supertile_size=4096 \
#     --supertile_folder=data/area/super_tiles/ \
#     --output_folder=data/area/color_detect \
#     --hsv_lower=38,33,56 \
#     --hsv_upper=126,121,224 \
#     --area=1000,950000 \
#     --kernel=6 \
#     --tags=class=grass_shrub \
#     --tags=project=LULC_labeling \
#     --tags=aoi=detroit \
#     --geojson_output=data/area_grass.geojson
# zip data/area_grass.zip data/area/super_tiles/*.geojson
