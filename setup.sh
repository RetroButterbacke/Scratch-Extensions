#!/bin/bash
set -e

echo "Verifying location of Scratch source is known"
if [ -z "$SCRATCH_SRC_HOME" ]; then
    echo "Error: SCRATCH_SRC_HOME environment variable is not set."
    exit 1
fi

EXTENSIONS_GUI_PATH="$SCRATCH_SRC_HOME/scratch-gui/src/lib/libraries/extensions"
EXTENSIONS_PATH="$SCRATCH_SRC_HOME/scratch-vm/src/extensions"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

[ ! -d "$EXTENSIONS_GUI_PATH/retrobutterbacke_pong_mp_connect/" ] && mkdir -p "$EXTENSIONS_GUI_PATH/retrobutterbacke_pong_mp_connect/"

if ! ls -l "$EXTENSIONS_GUI_PATH/retrobutterbacke_pong_mp_connect/linked" &> /dev/null; then
    cd "$EXTENSIONS_GUI_PATH/retrobutterbacke_pong_mp_connect/"
    ln -s "$DIR/Pong_background.png" background.png
    ln -s "$DIR/Pong_icon.png" icon.png
    touch linked
    cd $DIR
fi

if ! ls -l "$EXTENSIONS_PATH/retrobutterbacke_pong_mp_connect_linked" &> /dev/null; then
    cd $EXTENSIONS_PATH
    ln -s $DIR/retrobutterbacke_pong_mp_connect/ retrobutterbacke_pong_mp_connect
    touch retrobutterbacke_pong_mp_connect_linked
    cd $DIR
else
    rm -rf $EXTENSIONS_PATH/retrobutterbacke_pong_mp_connect
    cd $EXTENSIONS_PATH
    ln -s $DIR/retrobutterbacke_pong_mp_connect/ retrobutterbacke_pong_mp_connect
    touch retrobutterbacke_pong_mp_connect_linked
    cd $DIR
fi