for file in *.jpg; do
  convert "$file" \
    -gravity center -crop 640x640+0+0 +repage \
    -quality 85 \
    -define webp:method=6 \
    -strip \
    "${file%.*}.webp"
done
