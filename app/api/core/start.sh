#!/bin/bash
# 生产环境启动脚本
UVICORN_WORKERS=${UVICORN_WORKERS:-$(( $(nproc) * 2 + 1 ))}
echo "Starting EDBO API with $UVICORN_WORKERS workers"

uvicorn main:app \
--host 0.0.0.0 \
--port 8000 \
--workers $UVICORN_WORKERS \
--timeout-keep-alive 30 \
--no-access-log \
--http httptools
