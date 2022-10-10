#!/bin/bash
set -e

if [ -z "$1" ]
then
  image_version='latest'
else
  # Strip prefix from tag name so that v3.7.5 becomes 3.7.5
  image_version=${1#v}
fi

echo "$WALDUR_DOCKER_HUB_PASSWORD" | docker login -u "$WALDUR_DOCKER_HUB_USER" --password-stdin

if [ $CI_COMMIT_SHA ]
then
  echo "[+] Adding CI_COMMIT_SHA to docker/rootfs/COMMIT_SHA file"
  echo $CI_COMMIT_SHA > COMMIT
fi

if [ $CI_COMMIT_TAG ]
then
  echo "[+] Adding CI_COMMIT_TAG to docker/rootfs/COMMIT_TAG file"
  echo $CI_COMMIT_TAG > COMMIT_TAG
fi

docker build -t opennode/$CI_PROJECT_NAME:$image_version .
docker push "docker push opennode/$CI_PROJECT_NAME:$image_version"
docker images
