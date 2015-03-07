#!/bin/bash


BASEPATH=/mnt/mr_candie_nas/Geodaten/ch/zh/are/hoehen/2014/dsm_on_steroids/class_4/relief/

for FILE in ${BASEPATH}*.tif
do
  BASENAME=$(basename $FILE .tif)
  
  echo "Processing: ${FILE}"

  sudo gdalinfo -stats -hist $FILE
    #convert -channel R -gamma 2 -channel B -gamma 0.95 ${BASEPATH}/${BASENAME}.tif $OUTFILE_TMP
    

done



