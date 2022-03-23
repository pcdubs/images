#!/bin/bash

# This script uploads all files from ARTIFACTS folder to S3

S3_URL="s3://image-builder-ci-artifacts/osbuild-composer/$CI_COMMIT_BRANCH/$CI_JOB_ID/"
BROWSER_URL="https://s3.console.aws.amazon.com/s3/buckets/image-builder-ci-artifacts?region=us-east-1&prefix=osbuild-composer/$CI_COMMIT_BRANCH/$CI_JOB_ID/&showversions=false"
ARTIFACTS=${ARTIFACTS:-/tmp/artifacts}

# Colorful output.
function greenprint {
  echo -e "\033[1;32m[$(date -Isecond)] ${1}\033[0m"
}

sudo dnf -y install s3cmd
greenprint "Job artifacts will be uploaded to: $S3_URL"

AWS_SECRET_ACCESS_KEY="$V2_AWS_SECRET_ACCESS_KEY" \
AWS_ACCESS_KEY_ID="$V2_AWS_ACCESS_KEY_ID" \
s3cmd --acl-private put "$ARTIFACTS"/* "$S3_URL"

greenprint "Please login to 438669297788 AWS account and visit $BROWSER_URL to access job artifacts."
