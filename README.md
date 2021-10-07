# Vectorizing color range

This repo contains a bunch of script that allow to find change color in images using openCV, and then convert them  into geo vectors.


## How to use it? 

- Finding the right [HSV](https://en.wikipedia.org/wiki/HSL_and_HSV) values, in this example we are going to use  to find range color for trees.

```sh
    python src/hsv_color_picker.py --image_file=data/tree.png
```

And then find the ranges, playing with the values and clicking the HVS image

![image](https://user-images.githubusercontent.com/1152236/136305432-35006ee1-0e0a-4e38-a08c-f95e9c106009.png)


The output will be in the console, we will use that to run in large areas.

```
    --hsv_lower=31,25,9 \
    --hsv_upper=131,125,189 \
    --area=2000,50000 \
    --kernel=2 \
```

- Extract range value for an area.

```sh
docker run --rm -v ${PWD}:/mnt developmentseed/vector_color:v1 python src/range.py \
    --geojson_tiles_file=data/tiles.geojson \
    --output_folder=data/tiles/ \
    --url_map_service="https://tile.openstreetmap.org/{z}/{x}/{y}.png" \
    --hsv_lower=20,3,15 \
    --hsv_upper=75,145,191 \
    --area=2000,10000 \
    --kernel=2 \
    --tags=class=tree \
    --geojson_output=data/tree.geojson
```

Output 👇

![2021-10-06 21 17 42_fixed](https://user-images.githubusercontent.com/1152236/136309998-2af1423f-d447-4021-8ddd-412c9b1076b0.gif)
