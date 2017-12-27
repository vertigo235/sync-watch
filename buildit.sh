#!/bin/bash
rm -R syncwatch
cp -R /volume1/Resilio/EclipseWorkspace/sync-control ./syncwatch
docker build -t syncwatch:v4 /volume1/docker/syncwatch
