#!/bin/bash +x

# Tree Canopy
python src/range.py \
    --img_file="fixture/141155-193764-19.jpeg" \
    --hsv_lower="33,44,50" \
    --hsv_upper="97,131,164"
