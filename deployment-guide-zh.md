# EDBO 项目阿里云部署指南

## 一、服务器准备
1. 创建ECS实例
   - 推荐配置：2核4G（突发性能实例t5） 
   - 系统镜像：Ubuntu 22.04 LTS
   - 安全组开放端口：22, 80, 443, 8000

2. 系统初始化
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y git nginx python3-pip nodejs npm certbot python3-certbot-nginx

# 配置Python虚拟环境
sudo pip3 install virtualenv
```

## 二、后端服务部署
1. 克隆项目
```bash
cd /opt
sudo git clone https://your-git-repo.com/edbo-web.git
sudo chown -R ubuntu:ubuntu edbo-web
```

2. 配置环境变量
复制 `.env.production` 文件到项目目录：
```bash
cp edbo-web/app/api/core/.env.production edbo-web/app/api/core/.env
```

3. 安装依赖
```bash
cd edbo-web/app/api/core
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. 配置系统服务
创建`/etc/systemd/system/edbo-api.service`：
```ini
[Unit]
Description=EDBO API Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/edbo-web/app/api/core
Environment="PATH=/opt/edbo-web/app/api/core/venv/bin"
ExecStart=/opt/edbo-web/app/api/core/venv/bin/uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers $(( $(nproc) * 2 + 1 )) \
    --timeout-keep-alive 30 \
    --no-access-log \
    --http httptools

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start edbo-api
sudo systemctl enable edbo-api
```

## 三、前端部署
1. 安装依赖
```bash
cd /opt/edbo-web/app/web
npm install
npm run build
```

2. 配置环境变量
复制 `.env.production` 文件到项目目录：
```bash
cp edbo-web/app/web/.env.production edbo-web/app/web/.env
```

3. 配置Nginx
创建`/etc/nginx/sites-available/edbo-web`：
```nginx
server {
    listen 80;
    server_name xzsbo.xyz www.xzsbo.xyz;

    location / {
        root /opt/edbo-web/app/web/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/edbo-web /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

3. 配置SSL证书
```bash
sudo certbot --nginx -d xzsbo.xyz -d www.xzsbo.xyz
```

## 四、验证部署
1. 服务状态检查
```bash
systemctl status edbo-api  # 后端服务
certbot certificates        # SSL证书
nginx -t                    # Nginx配置
```

2. 访问测试
```bash
curl -I https://xzsbo.xyz
curl -I https://xzsbo.xyz/api/health-check
```

## 五、运维监控
1. 日志查看
```bash
journalctl -u edbo-api -f  # 后端日志
tail -f /var/log/nginx/access.log  # 访问日志
tail -f /var/log/nginx/error.log   # 错误日志
```

2. 进程守护
```bash
# 设置每日日志轮转
sudo nano /etc/logrotate.d/edbo-api
```
在 `/etc/logrotate.d/edbo-api` 中添加以下内容：
```ini
/opt/edbo-web/app/api/core/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 ubuntu ubuntu
}
```

3. 资源监控
建议安装：
- Prometheus + Grafana 监控系统资源
- Uptime Kuma 服务状态监控

## 六、备份策略
1. 数据库备份（如果使用数据库）
```bash
# 使用cron作业定期备份数据库
sudo crontab -e
```
在crontab中添加以下行以每天凌晨2点备份数据库：
```bash
0 2 * * * /usr/bin/pg_dump -U dbuser dbname > /opt/edbo-web/backups/db_backup_$(date +\%Y-\%m-\%d).sql
```

2. 代码备份
```bash
# 使用cron作业定期备份代码
sudo crontab -e
```
在crontab中添加以下行以每周日凌晨3点备份代码：
```bash
0 3 * * 0 tar -czvf /opt/edbo-web/backups/code_backup_$(date +\%Y-\%m-\%d).tar.gz /opt/edbo-web
```

## 七、安全加固建议
1. 更新系统和软件
```bash
sudo apt update && sudo apt upgrade -y
```

2. 配置防火墙
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw enable
```

3. 使用强密码和SSH密钥
确保使用强密码和SSH密钥进行服务器访问。

4. 定期检查日志
```bash
sudo journalctl -xe
sudo tail -f /var/log/auth.log
```

## 八、故障排查和日志管理
1. 检查服务状态
```bash
systemctl status edbo-api
sudo nginx -t
```

2. 查看日志
```bash
journalctl -u edbo-api -f
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

3. 使用日志分析工具
可以使用ELK Stack（Elasticsearch, Logstash, Kibana）进行日志分析。

## 九、更新策略
1. 代码更新流程
```bash
cd /opt/edbo-web
git pull origin main
# 重新部署前端
cd app/web && npm run build
# 重启后端
sudo systemctl restart edbo-api
