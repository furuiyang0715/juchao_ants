#!/bin/bash
# pack
USER=$1
HOST=$2
PROJ=juchao_ant
# 服务器分配的服务帐号
SERVER_NAME=pyspider
# 打包文件名 
DEPLOY_FILE="$PROJ.tar.gz"
# 打包文将相对路径
DEPLOY_FILE_PATH="out/$DEPLOY_FILE"
DEPLOY_DIR="~"

#######################################################################################################################
#              					      配置相关说明                                                    #
# DEPLOY_FILE_PATH 对应pack打包的文件路径									      #
# 项目路径/out/index_service.tar.gz  我这里pack.sh脚本打包的文件在项目的out目录下，如果位置和名称不对应需要调整。     #
#                                                                                                                     #
# 我这里服务器的部署路径为 ~/sentimentsrv/Release/sentimentsrv                                                        #
# 服务部署的路径为 ~ 路径，因为 DEPLOY_DIR=~                                                                          #
# 第二个sentimentsrv为服务运行的程序名称，因此SERVER=sentimentsrv                                                     #
# 不同的部署路径和服务名称需要根据对应的服务进行调整。                                                                #
#######################################################################################################################


echo "user:$USER"
echo "host:$HOST"
echo "project:$PROJ"

# 执行打包脚本
sh pack.sh $3

# 判断要上传部署的打包文件是否存在
if [ ! -f "$DEPLOY_FILE_PATH" ];then
	echo "$DEPLOY_FILE_PATH is not exist!"
	exit
fi
# 判断LDAP用户名是否已输入，登陆堡垒机需要
if [ -z "$USER" ];then
  echo "Please input your LDAP name!"
  exit
fi
# 判断部署的服务器名称，堡垒机设置的服务的唯一名称
if [ -z "$HOST" ];then
  echo "Please input deploy host!"
  exit
fi

# 上传部署文件,上传至home目录
function copydata()
{
    target=$DEPLOY_FILE_PATH
    user=$USER
    server=$HOST
    servername=$SERVER_NAME
    upload_path=/favorite/${server}/${servername}
    echo "ls" | sftp -b - -P42222 ${user}@jumpserver.jingzhuan.cn
    if [ $? -ne 0 ]
    then
       sftp -P42222 ${user}@jumpserver.jingzhuan.cn <<EOF
       quit
EOF
    fi
    echo "cd ${upload_path}" | sftp -b - -P42222 ${user}@jumpserver.jingzhuan.cn 
    if [ $? -ne 0 ]
    then
       upload_path=/favorite/${server}
    fi
    echo "cd ${upload_path}" | sftp -b - -P42222 ${user}@jumpserver.jingzhuan.cn 
    if [ $? -ne 0 ]
    then
       echo "Please add the server:$server to the favorite!(My assets -> Action -> Set Star)";
       exit;
    fi
    sftp -P42222 ${user}@jumpserver.jingzhuan.cn <<EOF
    cd ${upload_path}
    put ${target} ./
    quit
EOF
}

# 执行上传部署文件
copydata
# 执行部署脚本
expect -f ssh_to_jumper.exp $USER $HOST """
if [ ! -f \"$DEPLOY_FILE\" ];then
   echo '$DEPLOY_FILE is not exist! Please re-excute deploy shell!';
   exit;
fi 
cd $DEPLOY_DIR
if [ \"\$(pwd)\" != \"\$(pwd ~)\" ]
then
    echo 'TIP: the deploy file path not equal deploy dir, so move the deploy file!'
    mv ~/$DEPLOY_FILE ./
fi
tar -zxvf $DEPLOY_FILE ; 
rm -f $DEPLOY_FILE
"""
