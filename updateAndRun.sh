SCRIPT_PATH="Documents/P1_A_G10"
FILE_PATH="Documents/P1_A_G10/test.py"
CURRENT_DIR=$(pwd)

if [[ $SCRIPT_PATH != $CURRENT_DIR ]]; then
    cd "$Documents/P1_A_G10"
fi

git pull
python $FILE_PATH
