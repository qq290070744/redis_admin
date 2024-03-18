tag=20240318
docker build -t registry.cn-shanghai.aliyuncs.com/jwh/redis_admin:$tag .
docker push registry.cn-shanghai.aliyuncs.com/jwh/redis_admin:$tag
echo $tag
