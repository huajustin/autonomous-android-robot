SCRIPT_PATH="Documents/P1_A_G10"
CURRENT_DIR=$(pwd)

if [[ $SCRIPT_PATH != $CURRENT_DIR ]]; then
    cd "$Documents/P1_A_G10"
fi

git pull
python test.py 
