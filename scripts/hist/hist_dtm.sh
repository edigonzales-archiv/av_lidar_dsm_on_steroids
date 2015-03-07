#!/bin/bash


BASEPATH=/home/stefan/tmp/dsm_on_steroids/dtm/relief/50cm/

for FILE in ${BASEPATH}*.tif
do
  BASENAME=$(basename $FILE .tif)
  
  echo "Processing: ${FILE}"

  gdalinfo -stats -hist $FILE
    #convert -channel R -gamma 2 -channel B -gamma 0.95 ${BASEPATH}/${BASENAME}.tif $OUTFILE_TMP
    

done



