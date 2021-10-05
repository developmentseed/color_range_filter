#!/bin/bash +x



VECTOR_COLOR="docker run --rm -v ${PWD}:/mnt developmentseed/vector_color:v1"
GEOKIT_NODE="docker run --rm -v ${PWD}:/mnt/data/ developmentseed/geokit:node.latest"
# VECTOR_COLOR=""
# aws s3 sync s3://ds-data-projects/lulc/detroid/ data/detroid/
# # Tree Canopy

FOLDER=data/tiles_20
rm ${FOLDER}/*_output.png
rm ${FOLDER}/*.geojson

for img in ${FOLDER}/*.png; 
do
    echo ${img}
    set -x
    $VECTOR_COLOR python /range.py \
        --img_file=${img} \
        --hue=20,75 \
        --value=3,145 \
        --saturation=15,191 \
        --area=100,100000 \
        --kernel=3 \
        --tags=class=tree_canopy \
        --tags=project=LULC_labeling \
        --tags=aoi=detroit
        # --supertile=True \
        # --supertile_size=512 \
    set +x
done

echo '{"type": "FeatureCollection","features": []}' >data/tree_canopy.geojson
for geojson in ${FOLDER}/*.geojson;
do 
    echo ${geojson}
    ${GEOKIT_NODE} geojson-merge data/tree_canopy.geojson $geojson > data/tmp.geojson
    mv data/tmp.geojson data/tree_canopy.geojson
done





# python src/obj_recognizion.py  \
# --img_file=data/20_512/281879-388244-20-st.png \
# --hue=66,75 \
# --value=55,145 \
# --saturation=50,191