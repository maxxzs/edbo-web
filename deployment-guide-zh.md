# EDBO 云服务器部署指南

## 一、服务器准备（Ubuntu 22.04 LTS）
```bash
# 1. 系统更新
sudo apt update && sudo apt upgrade -y

# 2. 安装基础依赖
sudo apt install -y python3-pip python3-venv nginx git unzip ufw

# 3. 配置防火墙
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 4. 创建服务账户
sudo useradd -r -s /bin/false edbo_user
```

## 二、项目部署
```bash
# 1. 创建项目目录
sudo mkdir -p /opt/edbo/{app,static,data}
sudo chown -R edbo_user:www-data /opt/edbo

# 2. 克隆项目代码
sudo -u edbo_user git clone https://your-git-repo.com/edbo-web.git /opt/edbo/app

# 3. 安装Python依赖
cd /opt/edbo/app/api/core
sudo -u edbo_user python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 三、服务配置
1. 创建systemd服务文件 `/etc/systemd/system/edbo.service`：
```ini
[Unit]
Description=EDBO Optimization API
After=network.target

[Service]
User=edbo_user
Group=www-data
WorkingDirectory=/opt/edbo/app/api/core
Environment=CORS_ORIGINS=https://your-domain.com
Environment=UVICORN_WORKERS=4
ExecStart=/opt/edbo/app/api/core/start.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

2. 启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable edbo
sudo systemctl start edbo
```

## 四、Nginx配置
1. 创建配置文件 `/etc/nginx/sites-available/edbo` （项目根目录已提供nginx.conf模板）
2. 启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/edbo /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## 五、HTTPS配置（Let's Encrypt）
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 六、验证部署
```bash
# 检查服务状态
sudo systemctl status edbo

# 测试API接口
curl -X GET http://localhost:8000/api/v1/health
