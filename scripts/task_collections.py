'''
docker build -f Dockerfile -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/annspider:v1 .

docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/annspider:v1

sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/annspider:v1

sudo docker run --log-opt max-size=10m --log-opt max-file=3 \
-itd --name annspider --env LOCAL=0 \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/annspider:v1 \
python main.py
'''
