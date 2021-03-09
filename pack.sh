#!/bin/sh
if [ ! -d out  ];then
    mkdir out
fi

if [ -d tmp_conf ];then
    rm -rf tmp_conf
fi

rm -f out/juchao_ant.tar.gz

# tar -zxf 压缩包名.tar.gz
tar -zvcf  out/hkland_data_pro.tar.gz  \
            --exclude=../juchao_ant/out \
             --exclude=../*temp \
            --exclude=../*.pyc \
            --exclude=../*.git \
            --exclude=../*.idea \
            --exclude=../*__pycache__ \
            ../juchao_ant

rm -rf tmp_conf
