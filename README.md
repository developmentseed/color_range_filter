# Vectorizing color range

This repo contains a script that allows us to find range of colors in images using openCV, and then convert them into geo vectors.

# Install

```
git clone https://github.com/developmentseed/color_range_filter.git
cd color_range_filter/
docker-compose build
```


## How to use it? 

In order to use this script we need to find first the [HSV](https://en.wikipedia.org/wiki/HSL_and_HSV) , kernek and area values. 

Execute the HSV color picker with the follow script

```sh
    python src/hsv_color_picker.py --image_file=data/141013-193791-19-st.png
```

**Require:** The images that we pass to the script should be named as `{x}-{y}-{z}.png`  for tiles and `{x}-{y}-{z}-st.png` for [super-tiles](https://github.com/developmentseed/super_tiles)


Once the script is running, it will appear two windows, one of the image and the other for some other adjustments.

![image](https://user-images.githubusercontent.com/1152236/136613238-f8e392c4-d1df-4c04-afb4-6d5fae686723.png)

Where: 
- Area: To adjust the area of the color classification.
- Eval color Range: This is for adjusting the range of color to take the HSV values.
- Kernel: Describes how the pixels involved in the computation are combined in order to obtain the desired result.
- Crop image range: In some cases we may need only the area to work on, the maximum - 20  value means take all the image to get the color classification.

- In the image Window, click the area where you want to select: eg. 👇, Finding grass:

![image](image/color_picker_fixed.gif)

<!-- ![image](https://user-images.githubusercontent.com/1152236/136305432-35006ee1-0e0a-4e38-a08c-f95e9c106009.png) -->


- Once you have the desire selection , press key `e` and it will export a geojson file at same path of the image, and then it can be loaded in Qgis or JOSM.


![image](https://user-images.githubusercontent.com/1152236/136615507-82f76ea8-dd17-47bb-b9a3-d4978ee067e7.png)


# Runing the scrpit for large areas

For running in large area it is necessary to HSV, kernel and area values, it can be obtained from the console log in the previous step. E.g. The below values are for finding trees in urban areas.

```
    --hsv_lower=31,25,9 \
    --hsv_upper=131,125,189 \
    --area=2000,50000 \
    --kernel=2 \
```

- Use the following values in the script 👇

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
