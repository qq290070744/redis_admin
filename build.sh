tag=20240307.4
docker build -t registry.cn-shanghai.aliyuncs.com/jwh/redis_admin:$tag .
docker push registry.cn-shanghai.aliyuncs.com/jwh/redis_admin:$tag
echo $tag
