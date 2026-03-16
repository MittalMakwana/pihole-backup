import os
import glob
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from pihole_backup.config import load_config
from pihole_backup.logger import setup_logger


def get_s3_client(s3_cfg: dict):
    return boto3.client(
        "s3",
        region_name=s3_cfg["region"],
        aws_access_key_id=s3_cfg["access_key"],
        aws_secret_access_key=s3_cfg["secret_key"],
    )


def generate_backup(backup_dir: str, logger) -> str:
    logger.info("Generating Pi-hole teleporter backup...")

    # Ensure backup dir exists
    os.makedirs(backup_dir, exist_ok=True)

    # Run teleporter with cwd set to backup_dir so zip lands there
    result = subprocess.run(
        ["sudo", "pihole-FTL", "--teleporter"],
        capture_output=True,
        text=True,
        cwd=backup_dir
    )

    if result.returncode != 0:
        logger.error(f"pihole-FTL failed: {result.stderr}")
        sys.exit(1)

    pattern = os.path.join(backup_dir, "pi-hole_*.zip")
    files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)

    if not files:
        logger.error(f"No backup zip found in {backup_dir}")
        sys.exit(1)

    logger.info(f"Backup created: {files[0]}")
    return files[0]

def upload_to_s3(backup_file: str, s3_cfg: dict, logger) -> None:
    s3 = get_s3_client(s3_cfg)
    filename = os.path.basename(backup_file)
    s3_key = f"{s3_cfg['prefix']}/{filename}"

    logger.info(f"Uploading to s3://{s3_cfg['bucket']}/{s3_key}...")

    try:
        s3.upload_file(backup_file, s3_cfg["bucket"], s3_key)
        logger.info(f"Upload successful: s3://{s3_cfg['bucket']}/{s3_key}")
    except (BotoCoreError, ClientError) as e:
        logger.error(f"S3 upload failed: {e}")
        sys.exit(1)


def cleanup_old_backups(s3_cfg: dict, retention_days: int, logger) -> None:
    s3 = get_s3_client(s3_cfg)
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)

    logger.info(f"Cleaning up backups older than {retention_days} days...")

    try:
        response = s3.list_objects_v2(
            Bucket=s3_cfg["bucket"],
            Prefix=s3_cfg["prefix"]
        )

        deleted = 0
        for obj in response.get("Contents", []):
            if obj["LastModified"] < cutoff:
                s3.delete_object(Bucket=s3_cfg["bucket"], Key=obj["Key"])
                logger.info(f"Deleted old backup: {obj['Key']}")
                deleted += 1

        logger.info(f"Cleanup complete — {deleted} backup(s) deleted")

    except (BotoCoreError, ClientError) as e:
        logger.error(f"S3 cleanup failed: {e}")


def list_backups(args) -> None:
    config = load_config()
    s3_cfg = config["s3"]
    s3 = get_s3_client(s3_cfg)

    response = s3.list_objects_v2(
        Bucket=s3_cfg["bucket"],
        Prefix=s3_cfg["prefix"]
    )

    objects = response.get("Contents", [])
    if not objects:
        print("No backups found in S3.")
        return

    print(f"\n{'File':<60} {'Size':>10} {'Last Modified'}")
    print("-" * 90)
    for obj in sorted(objects, key=lambda x: x["LastModified"], reverse=True):
        name = obj["Key"].split("/")[-1]
        size = f"{obj['Size'] / 1024:.1f} KB"
        date = obj["LastModified"].strftime("%Y-%m-%d %H:%M:%S")
        print(f"{name:<60} {size:>10} {date}")
    print()


def create_backup(args) -> None:
    config = load_config()
    logger = setup_logger(config["backup"]["log_file"])

    logger.info("=" * 50)
    logger.info("Pi-hole Backup Started")
    logger.info("=" * 50)

    backup_file = generate_backup(config["backup"]["backup_dir"], logger)
    upload_to_s3(backup_file, config["s3"], logger)

    os.remove(backup_file)
    logger.info(f"Deleted local file: {backup_file}")

    cleanup_old_backups(config["s3"], config["backup"]["retention_days"], logger)

    logger.info("Pi-hole backup completed successfully ✓")
