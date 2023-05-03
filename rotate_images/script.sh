#!/bin/bash

### PARSE ARGUMENTS
while [ $# -gt 0 ] ; do
  case $1 in
    -s | --src) src="$2" ;;
    -d | --dst) dst="$2" ;;
    -r | --rotate_angle) rotate_angle="$2" ;;

  esac
  shift
done

echo $src $dst, $rotate_angle



### Pocess ffmpeg rotate
for pathname in "$src/"*;  # "${src}/*.jpg"
do
    base_path=$(basename "$pathname")
    echo "base_path $base_path"
    ffmpeg -i "${src}${base_path}" -vf "rotate=${rotate_angle}*PI/180" "${dst}${base_path}"
    # ffmpeg -i "${src}${base_path}" -vf "transpose=1" "${dst}${base_path}"

done
