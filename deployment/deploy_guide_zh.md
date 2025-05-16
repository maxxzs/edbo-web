# EDBO 实验优化平台部署指南

## 服务器要求
- 操作系统: Ubuntu 22.04 LTS
- 硬件配置: 2核CPU / 2GB内存 / 20GB存储
- 网络要求:
  - 开放端口: 22(SSH), 80(HTTP), 443(HTTPS), 8000(API)
  - 域名: xzsbo.xyz (已配置DNS解析)

## 1. 服务器初始化
```bash
# 系统更新
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y git nginx build-essential libssl-dev

# 配置防火墙
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 2. 环境配置
### 2.1 Conda环境
```bash
# 安装Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda
eval "$($HOME/miniconda/bin/conda shell.bash hook)"
conda init

# 创建Python环境
conda create -n edbo_env python=3.9 -y
conda activate edbo_env
conda install -c conda-forge numpy pandas scikit-learn -y
pip install "fastapi[all]" uvicorn python-multipart pandas
```

### 2.2 Node.js环境
```bash
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs
```

## 3. 项目部署
### 3.1 克隆代码
```bash
sudo mkdir -p /opt/edbo-web
sudo chown -R $USER:$USER /opt/edbo-web
git clone https://github.com/your-repo/edbo-web.git /opt/edbo-web
```

### 3.2 配置文件
`config/production.env`:
```env
VITE_API_BASE_URL=https://xzsbo.xyz/api
UVICORN_WORKERS=2
CORS_ORIGINS=https://xzsbo.xyz
```

## 4. 服务配置
### 4.1 后端服务 (Systemd)
`/etc/systemd/system/edbo.service`:
```ini
[Unit]
Description=EDBO API Service
After=network.target

[Service]
User=www-data
Environment="PATH=/home/ubuntu/miniconda/envs/edbo_env/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/home/ubuntu/miniconda/envs/edbo_env/bin/uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --ssl-keyfile /etc/letsencrypt/live/xzsbo.xyz/privkey.pem \
    --ssl-certfile /etc/letsencrypt/live/xzsbo.xyz/fullchain.pem \
    --proxy-headers \
    --forwarded-allow-ips="*"
WorkingDirectory=/opt/edbo-web/app/api/core
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4.2 前端配置 (Nginx)
`/etc/nginx/sites-available/xzsbo.xyz`:
```nginx
server {
    listen 80;
    server_name xzsbo.xyz;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name xzsbo.xyz;
    
    ssl_certificate /etc/letsencrypt/live/xzsbo.xyz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/xzsbo.xyz/privkey.pem;
    
    location / {
        root /opt/edbo-web/app/web/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 5. 启动服务
```bash
# 后端服务
sudo systemctl daemon-reload
sudo systemctl enable edbo
sudo systemctl start edbo

# 前端构建
cd /opt/edbo-web/app/web
npm install
npm run build

# Nginx配置
sudo ln -s /etc/nginx/sites-available/xzsbo.xyz /etc/nginx/sites-enabled/
sudo systemctl reload nginx

# SSL证书
sudo snap install --classic certbot
sudo certbot --nginx -d xzsbo.xyz
```

## 验证部署
```bash
# 检查服务状态
systemctl status edbo nginx

# 测试API端点
curl -k https://xzsbo.xyz/api/v1/health

# 查看实时日志
journalctl -u edbo -f
