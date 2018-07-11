#!/bin/sh

cd doc

LOCAL_CONF="source/conf.py"
REPO_DOC_ROOT="doc/source"
LOCAL_BUILD_DIR="build/html/"
SPHINX_OPTS="-D templates_path=$PWD/source/_templates"

sphinx-versioning -l $LOCAL_CONF --install-versions build $REPO_DOC_ROOT $LOCAL_BUILD_DIR -- $SPHINX_OPTS
