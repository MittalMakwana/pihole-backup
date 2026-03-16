from pihole_backup.config import init_config, show_config


def handle_config(args):
    if args.action == "init":
        init_config()
    elif args.action == "show":
        show_config()
