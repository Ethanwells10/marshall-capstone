# Marshall Capstone - Deployment Guide

This guide walks you through completing the full deployment of your Hello World application.

## Current Status ✅

**Completed:**
- ✅ Project structure with React frontend and Go backend
- ✅ AWS Lightsail instance running (18.219.9.8)
- ✅ Frontend deployed and accessible at http://18.219.9.8
- ✅ Backend built and running as systemd service on port 8080
- ✅ Nginx configured as reverse proxy
- ✅ GitHub repository: https://github.com/Ethanwells10/marshall-capstone
- ✅ GitHub Actions workflow file created

**Endpoints Working:**
- Frontend: http://18.219.9.8/
- Backend Health: http://18.219.9.8/health

## Remaining Steps

### Step 1: Assign Static IP in Lightsail

1. Go to https://lightsail.aws.amazon.com/
2. Click on your instance
3. Click "Networking" tab
4. Under "IPv4 Firewall", ensure these ports are open:
   - HTTP (80)
   - HTTPS (443)
   - SSH (22)
5. Under "Static IP", click "Create static IP"
   - If 18.219.9.8 is already static, you're done!
   - If not, attach a static IP to your instance

### Step 2: Register a Domain Name

**Option A: Cloudflare (Free)**
1. Go to https://www.cloudflare.com/
2. Sign up for a free account
3. Register a free domain or transfer an existing one
4. In Cloudflare Dashboard → DNS → Records:
   - Type: A
   - Name: @ (or your subdomain)
   - IPv4 address: 18.219.9.8
   - Proxy status: DNS only (gray cloud)
   - TTL: Auto

**Option B: Namecheap**
1. Go to https://www.namecheap.com/
2. Search for and purchase a domain
3. In Domain List → Manage → Advanced DNS:
   - Add A Record:
     - Host: @
     - Value: 18.219.9.8
     - TTL: Automatic

**DNS Propagation:**
Wait 5-60 minutes for DNS to propagate. Test with:
```bash
nslookup yourdomain.com
```

### Step 3: Install SSL Certificate (Let's Encrypt)

Once your domain points to your server:

```bash
# SSH into your server
ssh -i ~/.ssh/LightsailDefaultKey-us-east-2.pem ubuntu@18.219.9.8

# Install Certbot
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow the prompts:
# - Enter your email
# - Agree to terms of service
# - Choose redirect HTTP to HTTPS (option 2)

# Verify auto-renewal is set up
sudo certbot renew --dry-run

# Exit SSH
exit
```

Certbot will automatically:
- Obtain the SSL certificate
- Update nginx configuration
- Set up auto-renewal

### Step 4: Configure GitHub Secrets

1. Go to your repository: https://github.com/Ethanwells10/marshall-capstone
2. Click Settings → Secrets and variables → Actions
3. Click "New repository secret" and add:

**SERVER_IP:**
- Name: `SERVER_IP`
- Value: `18.219.9.8`

**SSH_PRIVATE_KEY:**
- Name: `SSH_PRIVATE_KEY`
- Value: Contents of `~/.ssh/LightsailDefaultKey-us-east-2.pem`

To get the private key:
```bash
cat ~/.ssh/LightsailDefaultKey-us-east-2.pem
```
Copy the entire output including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----`

### Step 5: Enable GitHub Actions

1. In your repository, go to Actions tab
2. If prompted, enable GitHub Actions
3. The workflow file `.github/workflows/deploy.yml` is already created
4. Make a small change to test deployment:

```bash
cd ~/marshall-capstone
echo "# Test deployment" >> README.md
git add README.md
git commit -m "Test GitHub Actions deployment"
git push origin main
```

5. Go to Actions tab to watch the deployment
6. If successful, your changes will be automatically deployed!

### Step 6: Verify HTTPS Access

After SSL is installed and DNS is configured:

```bash
# Test HTTPS access
curl -I https://yourdomain.com

# Should return:
# HTTP/2 200
# server: nginx/1.24.0 (Ubuntu)
# ...

# Test backend health endpoint
curl https://yourdomain.com/health

# Should return:
# {"status":"ok"}
```

## Server Configuration Details

### Services Running

**Frontend:**
- Location: `/var/www/hello-frontend`
- Served by: nginx
- Port: 80/443

**Backend:**
- Service: `marshall-backend.service`
- Binary: `/home/ubuntu/marshall-capstone/backend/backend`
- Port: 8080 (internal only)
- Managed by: systemd

**Nginx:**
- Config: `/etc/nginx/sites-available/marshall-capstone`
- Proxies `/health` and `/api/*` to backend
- Serves React app for all other routes

### Useful Commands

```bash
# Check backend service status
ssh -i ~/.ssh/LightsailDefaultKey-us-east-2.pem ubuntu@18.219.9.8 \
  "sudo systemctl status marshall-backend"

# View backend logs
ssh -i ~/.ssh/LightsailDefaultKey-us-east-2.pem ubuntu@18.219.9.8 \
  "sudo journalctl -u marshall-backend -f"

# Restart backend
ssh -i ~/.ssh/LightsailDefaultKey-us-east-2.pem ubuntu@18.219.9.8 \
  "sudo systemctl restart marshall-backend"

# Check nginx status
ssh -i ~/.ssh/LightsailDefaultKey-us-east-2.pem ubuntu@18.219.9.8 \
  "sudo systemctl status nginx"

# View nginx logs
ssh -i ~/.ssh/LightsailDefaultKey-us-east-2.pem ubuntu@18.219.9.8 \
  "sudo tail -f /var/log/nginx/access.log"
```

## Troubleshooting

### Backend not responding
```bash
ssh -i ~/.ssh/LightsailDefaultKey-us-east-2.pem ubuntu@18.219.9.8
sudo systemctl restart marshall-backend
sudo journalctl -u marshall-backend --no-pager -n 50
```

### Frontend not updating
```bash
ssh -i ~/.ssh/LightsailDefaultKey-us-east-2.pem ubuntu@18.219.9.8
cd ~/marshall-capstone/frontend
npm run build
sudo rm -rf /var/www/hello-frontend/*
sudo cp -r dist/* /var/www/hello-frontend/
```

### SSL certificate issues
```bash
ssh -i ~/.ssh/LightsailDefaultKey-us-east-2.pem ubuntu@18.219.9.8
sudo certbot certificates
sudo certbot renew --force-renewal
```

### GitHub Actions failing
- Check repository secrets are set correctly
- Ensure SSH key has proper permissions
- Review workflow logs in Actions tab

## Architecture Overview

```
Internet
   ↓
[Cloudflare/Domain] → [AWS Lightsail: 18.219.9.8]
                           ↓
                     [Nginx :80/:443]
                           ├─→ / → React Frontend (/var/www/hello-frontend)
                           ├─→ /health → Go Backend (:8080)
                           └─→ /api/* → Go Backend (:8080)
                                   ↓
                           [Go Backend Service]
                           (marshall-backend.service)
```

## Next Steps After Deployment

1. **Test everything works:**
   - Visit https://yourdomain.com
   - Check https://yourdomain.com/health
   - Make a code change and push to test CI/CD

2. **Monitor your application:**
   - Set up monitoring with AWS CloudWatch
   - Configure alerts for service failures
   - Monitor SSL certificate expiration

3. **Improve security:**
   - Configure firewall rules
   - Set up fail2ban for SSH protection
   - Enable automated backups in Lightsail

4. **Scale as needed:**
   - Upgrade Lightsail instance size
   - Add load balancer for high traffic
   - Set up database if needed

## Support

- AWS Lightsail Docs: https://lightsail.aws.amazon.com/ls/docs
- Let's Encrypt: https://letsencrypt.org/docs/
- Nginx Documentation: https://nginx.org/en/docs/
- GitHub Actions: https://docs.github.com/en/actions
