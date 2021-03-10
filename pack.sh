#!/bin/bash
PWD=$(pwd)
PROJECT="juchao_ant"
# copy target file
PACK_PATH="$PWD/target/$PROJECT"
if [ ! -d $PACK_PATH  ];then
    mkdir -p $PACK_PATH
fi

TARGET_FILE=$PWD/out/$PROJECT.tar.gz
# create target pack file
if [ ! -d $PWD/out  ];then
    mkdir -p $PWD/out
fi
if [ -f TARGET_FILE ];then
	rm -f $TARGET_FILE
fi

cp -rf ./*.py $PACK_PATH
cp -rf annversion1 $PACK_PATH
cp -rf annversion2 $PACK_PATH
cp -rf spy_announcement $PACK_PATH
cp requirements.txt $PACK_PATH
VERSION_FILE=version
git log --pretty=oneline -n 1 > $PACK_PATH/$VERSION_FILE

cd $PACK_PATH
tar -zcvf $TARGET_FILE ../$PROJECT \
                    --exclude=*.d \
                    --exclude=*.o \
                    --exclude=*/.git\
                    --exclude=*/logs \
                    --exclude=*.gitignore \
                    --exclude=*.ini \
                    --exclude=*.conf \
                    --exclude=*.heap \
                    --exclude=*.pdf \
                    --exclude=*.ldb \
                    --exclude=*.gitmodules
rm -rf $PACK_PATH
