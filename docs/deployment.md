# Deployment Guide

This guide walks you through the steps to deploy your application effectively.

## Prerequisites

Before you begin, ensure you have the following:

- Domain name registered
- Mailgun account for email services
- AWS access for S3
- VPS or server access for deployment (preferably Ubuntu-based)

---

## Step 1: AWS S3 Setup

### Create the S3 Bucket

1. Log in to your AWS Management Console.
2. Navigate to S3 and create a new bucket.
3. In "Block public access settings," only uncheck the following:
   - Block public access to buckets and objects granted through new access control lists (ACLs)
   - Block public access to buckets and objects granted through any access control lists (ACLs)
4. Click **"Create bucket"** to finalize the setup.

### IAM Policy Creation

1. In the IAM section, go to **Policies** → **Create policy**.
2. Use the following JSON policy to allow S3 access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListBucket",
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::<your-bucket-name>"
    },
    {
      "Sid": "AccessStaticMedia",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": [
        "arn:aws:s3:::<your-bucket-name>/static/*",
        "arn:aws:s3:::<your-bucket-name>/media/*"
      ]
    }
  ]
}
```

### IAM User Creation

1. Navigate to **IAM → Users** → **Add user**.
2. Enter user details.
3. Under the "Permissions" tab, choose **Attach existing policies directly**.
4. Attach the policy created above.
5. Complete the remaining steps and create the user.
6. After creation, go to the user's **Security credentials** tab.
7. Click **Create access key** and download the CSV file.

---

## Step 2: Mailgun Setup

1. Sign up for a Mailgun account.
2. Go to **Send → Domains → Add Domain**.
3. Fill in domain details.
4. Follow Mailgun's DNS instructions (usually adding TXT records for SPF and DKIM).
5. Once verified, Mailgun is ready for sending emails.

---

## Step 3: Domain Configuration

1. Log in to your domain registrar's control panel.
2. Go to your domain's DNS settings.
3. Add the following DNS records:
   - **A Record**: Point your domain/subdomain to your VPS IP address.
   - **TXT Records**: Add the SPF and DKIM records from Mailgun.
4. Save changes and allow up to 48 hours for DNS propagation.

> **Note**: If you want to receive emails, you will also need to configure MX records, which is beyond the scope of this guide.

---

## Step 4: Deploying Your Application

### Provision the Server

1. Choose a VPS provider (e.g., DigitalOcean, AWS EC2) and create a new instance.
2. SSH into your server.

```bash
ssh <your-username>@<your-server-ip>
```

3. Run basic setup:

```bash
sudo apt update && sudo apt upgrade
```

4. Configure UFW (firewall):

```bash
sudo ufw allow OpenSSH
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

### Install Required Packages

**Docker & Docker Compose**:

```bash
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
sudo usermod -aG docker <your-username>
```

> 💡 **Note**: Log out and log back in (or `reboot`) to apply Docker group changes.

**Make**:

```bash
sudo apt install make -y
```

### Application Setup

1. Create a directory for your project:

```bash
sudo mkdir -p /opt/django-oidc-provider
sudo chown -R <your-username>:<your-username> /opt/django-oidc-provider
```

2. Clone your repository:

```bash
cd /opt/django-oidc-provider
git clone https://github.com/<your-username>/django-oidc-provider.git .
```

3. Run the deployment commands:

```bash
make init
make init-ssl
make deploy
make migrate
# Optional:
make createsuperuser
```

> The first two commands will prompt you for configuration details such as domain name and Mailgun credentials. Provide the correct information as prompted.

4. Your application should now be live and accessible via your domain. 🚀

---

## Step 5: Post-Deployment

After deployment:

1. Visit your admin panel.
2. Read the [`applications.md`](applications.md) file to learn how to register and manage OAuth2 client applications.

---

### Security Considerations

#### Secure Docker Socket

> Important Note on Docker PermissionsThis guide adds your user to the docker group for ease of use. Be aware that this group effectively grants root access because Docker can run arbitrary commands and mount volumes. This might not be acceptable in an organization. Please make sure you are aligned with your organization's security policies.

#### Disclaimer

> This deployment guide is optimized for a single-tenant environment. It is your responsibility to ensure the configuration meets your organization’s security requirements. Review and adapt the instructions if you plan to run this in a shared or multi-user environment.

Your Django OIDC Provider application is now deployed and ready to use. If you encounter issues, please create an issue on [GitHub](https://github.com/dakshesh14/django-oidc-provider). For security-related concerns, use the recommended secure disclosure channels listed in the repository.
