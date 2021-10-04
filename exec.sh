#!/bin/bash +x

# Tree Canopy
python src/range.py \
    --img_file="fixture/141155-193764-19.jpeg" \
    --hue=20,75 \
    --value=3,145 \
    --saturation=15,191 \
    --area=200,420000 \
    --kernel=3