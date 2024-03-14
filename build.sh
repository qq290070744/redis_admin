tag=202403014.1
docker build -t registry.cn-shanghai.aliyuncs.com/jwh/redis_admin:$tag .
docker push registry.cn-shanghai.aliyuncs.com/jwh/redis_admin:$tag
echo $tag
