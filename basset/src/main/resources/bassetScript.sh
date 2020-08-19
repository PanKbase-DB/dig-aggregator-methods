#!/bin/bash -xe

echo "JOB_BUCKET     = ${JOB_BUCKET}"
echo "JOB_METHOD     = ${JOB_METHOD}"
echo "JOB_STAGE      = ${JOB_STAGE}"
echo "JOB_PREFIX     = ${JOB_PREFIX}"

#
# You can also pass command line arguments to the script from your stage.
#

echo "Argument passed: $*"

# set where the source and destination is in S3 and where VEP is
S3DIR="s3://dig-analysis-data/out/"

# get the name of the part file from the command line; set the output filename
PART=$(basename -- "$1")
OUTFILE="${PART%.*}.json"
WARNINGS="${OUTFILE}_warnings.txt"

# copy the part file from S3 to local
aws s3 cp "$S3DIR/varianteffect/variants/$PART" .

# run pytorch script
python3 fullBassetScript.py -i "$PART" -b 100 -o "$OUTFILE"

# copy the output of VEP back to S3
aws s3 cp "$OUTFILE" "$S3DIR/regionpytorch/$OUTFILE"

# delete the input and output files; keep the cluster clean
rm "$PART"
rm "$OUTFILE"

# check for a warnings file, upload that, too and then delete it
if [ -e "$WARNINGS" ]; then
    aws s3 cp "$WARNINGS" "$S3DIR/effects/warnings/$WARNINGS"
    rm "$WARNINGS"
fi

