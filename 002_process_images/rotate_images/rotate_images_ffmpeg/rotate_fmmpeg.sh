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

shopt -s extglob

### Pocess ffmpeg rotate
for pathname in "$src/"*;  # "${src}/*.jpg"
do
    base_path=$(basename "$pathname")
    echo "base_path $base_path"

    # Create path bash robustly
    src_tmp=("$src" "$base_path");
    src_tmp=$(printf '/%s' "${src_tmp[@]%/}" )
    echo "src_tmp $src_tmp"

    dst_tmp=("$dst" "$base_path");
    dst_tmp=$(printf '/%s' "${dst_tmp[@]%/}" )
    echo "dst_tmp $dst_tmp"

    ffmpeg -i $src_tmp -vf "rotate=${rotate_angle}*PI/180" $dst_tmp
    # ffmpeg -i "${src}${base_path}" -vf "transpose=1" "${dst}${base_path}"

done
