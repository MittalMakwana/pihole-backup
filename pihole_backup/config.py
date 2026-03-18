import yaml
from pathlib import Path

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "pihole-backup" / "config.yml"


def load_config(config_path: str = None) -> dict:
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found at {path}. "
            f"Run 'pihole-backup config init' to create one."
        )
    with open(path, "r") as f:
        return yaml.safe_load(f)


def init_config() -> None:
    DEFAULT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    if DEFAULT_CONFIG_PATH.exists():
        print(f"Config already exists at {DEFAULT_CONFIG_PATH}")
        return

    bucket      = input("Enter S3 bucket name: ").strip()
    prefix      = input("Enter S3 prefix (default: pihole): ").strip() or "pihole"
    region      = input("Enter S3 region (default: us-east-1): ").strip() or "us-east-1"
    access_key  = input("Enter AWS access key: ").strip()
    secret_key  = input("Enter AWS secret key: ").strip()
    retention   = input("Enter retention days (default: 90): ").strip() or "90"
    backup_dir  = input(f"Enter backup dir (default: {Path.home()}): ").strip() or str(Path.home())
    log_file    = input(
        f"Enter log file path (default: {Path.home()}/.logs/pihole-backup.log): "
    ).strip() or str(Path.home() / ".logs" / "pihole-backup.log")
    config = {
        "s3": {
            "bucket":     bucket,
            "prefix":     prefix,
            "region":     region,
            "access_key": access_key,
            "secret_key": secret_key,
        },
        "backup": {
            "retention_days": int(retention),
            "backup_dir":     backup_dir,
            "log_file":       log_file,
        }
    }

    with open(DEFAULT_CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print(f"Config saved to {DEFAULT_CONFIG_PATH}")


def show_config() -> None:
    config = load_config()
    # Mask secret key
    config["s3"]["secret_key"] = "***********"
    print(yaml.dump(config, default_flow_style=False))
