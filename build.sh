tag=202403018
docker build -t registry.cn-shanghai.aliyuncs.com/jwh/redis_admin:$tag .
docker push registry.cn-shanghai.aliyuncs.com/jwh/redis_admin:$tag
echo $tag
