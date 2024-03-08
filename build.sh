tag=20240308.5
docker build -t registry.cn-shanghai.aliyuncs.com/jwh/redis_admin:$tag .
docker push registry.cn-shanghai.aliyuncs.com/jwh/redis_admin:$tag
echo $tag
