# EDBO 混合部署方案指南

## 一、架构说明
- 前端：静态资源托管（Vercel/Netlify/GitHub Pages）
- 后端：独立云服务器API服务
- 通信：前端直接通过IP访问后端API

## 二、服务器准备（Ubuntu 22.04 LTS）
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

## 三、后端API部署
```bash
# 1. 创建项目目录
sudo mkdir -p /opt/edbo/{app,static,data}
sudo chown -R edbo_user:www-data /opt/edbo

# 2. 克隆项目代码
sudo -u edbo_user git clone https://your-git-repo.com/edbo-web.git /opt/edbo/app

# 3. 安装Python依赖
cd /opt/edbo/app/app/api/core
sudo -u edbo_user python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. 配置环境变量
echo "CORS_ORIGINS=*
UVICORN_WORKERS=4
RELOAD=false
HOST=0.0.0.0
PORT=8000" > .env

# 5. 启动服务（PM2守护进程）
sudo npm install -g pm2
pm2 start start.sh --name edbo-api
pm2 save
pm2 startup
```

## 四、前端部署
```bash
# 1. 进入前端目录
cd /opt/edbo/app/app/web

# 2. 安装依赖
npm install

# 3. 构建生产包（替换your-server-ip为实际IP）
VITE_API_BASE_URL=http://YOUR_SERVER_IP:8000 npm run build

# 4. 部署dist目录到静态托管平台
# （具体步骤根据托管平台文档操作）
```

## 五、Nginx反向代理配置
```nginx
server {
    listen 80;
    server_name YOUR_SERVER_IP;

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location / {
        root /opt/edbo/app/app/web/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

## 六、HTTPS配置（可选）
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 七、验证部署
```bash
# 检查API服务状态
pm2 list edbo-api

# 测试API接口
curl -X GET http://localhost:8000/api/v1/health

# 检查前端访问
curl -I http://your-server-ip
