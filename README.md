# pihole-backup

A simple CLI tool to backup Pi-hole v6 to AWS S3 (or any S3-compatible storage).

Inspired by [servarr-backup](https://github.com/Zerka30/servarr-backup).

## Features

- 🔒 Generates Pi-hole teleporter backup using `pihole-FTL --teleporter`
- ☁️  Uploads backup to AWS S3 (or S3-compatible storage)
- 🗑️  Automatic retention cleanup of old backups
- 📋 List backups stored in S3
- 📝 Logging to file and console
- ⚙️  Simple YAML config

## Requirements

- Python 3.11+
- Pi-hole v6
- AWS S3 bucket (or S3-compatible: Backblaze B2, Wasabi, Cloudflare R2)

## Installation
```bash
git clone https://github.com/YOUR_USERNAME/pihole-backup.git
cd pihole-backup
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Configuration
```bash
pihole-backup config init
```

This creates a config file at `~/.config/pihole-backup/config.yml`.

You can also copy the example config:
```bash
cp config.example.yml ~/.config/pihole-backup/config.yml
```

Example config:
```yaml
s3:
  bucket: "your-s3-bucket-name"
  prefix: "pihole"
  region: "us-east-1"
  access_key: "YOUR_ACCESS_KEY"
  secret_key: "YOUR_SECRET_KEY"

backup:
  retention_days: 90
  backup_dir: "/home/YOUR_USER/.backup"
  log_file: "/home/YOUR_USER/.logs/pihole-backup.log"
```

## Usage
```bash
# Create and upload a backup
pihole-backup backup create

# List backups in S3
pihole-backup backup ls

# Show current config
pihole-backup config show

# Show version
pihole-backup --version
```

## Automate with Cron

Run daily at 2:15am:
```bash
crontab -e
```

Add:
```
15 2 * * * /home/YOUR_USER/pihole-backup/venv/bin/pihole-backup backup create >> /home/YOUR_USER/.logs/pihole-backup.log 2>&1
```

## S3 IAM Policy

Minimum required AWS IAM policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

## License

MIT
