import argparse
import sys
from pihole_backup import __version__
from pihole_backup.commands.backup import create_backup, list_backups
from pihole_backup.commands.config_cmd import handle_config


def main():
    parser = argparse.ArgumentParser(
        prog="pihole-backup",
        description="Pi-hole v6 Backup Tool — Backup Pi-hole to AWS S3"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"pihole-backup v{__version__}"
    )

    subparsers = parser.add_subparsers(dest="command")

    # ── config ──────────────────────────────────────────
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_sub = config_parser.add_subparsers(dest="action")
    config_sub.add_parser("init", help="Initialize config interactively")
    config_sub.add_parser("show", help="Show current config")
    config_parser.set_defaults(func=handle_config)

    # ── backup ──────────────────────────────────────────
    backup_parser = subparsers.add_parser("backup", help="Backup operations")
    backup_sub = backup_parser.add_subparsers(dest="action")

    backup_sub.add_parser("create", help="Create and upload backup to S3") \
        .set_defaults(func=create_backup)

    backup_sub.add_parser("ls", help="List backups in S3") \
        .set_defaults(func=list_backups)

    # ── parse ────────────────────────────────────────────
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
