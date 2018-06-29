#!/bin/sh
set -e

LOCAL_CONF="doc/source/conf.py"
REPO_DOC_ROOT="doc/source"
LOCAL_BUILD_DIR="doc/build/html/"

sphinx-versioning -l $LOCAL_CONF build $REPO_DOC_ROOT $LOCAL_BUILD_DIR
