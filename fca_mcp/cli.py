import argparse
import logging
import sys

ENTERPRISE_MESSAGE = (
    "This command is available in the Enterprise edition. "
    "Schedule access at https://cal.com/trailblazelabs"
)


def configure_logging(level=logging.INFO, use_colors=True):
    """No-op basic logger for community edition."""
    logging.basicConfig(level=level, format="%(message)s")


def _enterprise_only(command_name: str) -> int:
    # Always print a clear message to stderr
    print(f"{command_name}: {ENTERPRISE_MESSAGE}", file=sys.stderr)
    logging.info("%s: %s", command_name, ENTERPRISE_MESSAGE)
    return 1


def create_parser():
    """Create and return the argument parser (interfaces only)."""
    parser = argparse.ArgumentParser(
        description="FCA MCP CLI (Community Edition) — interfaces only; no data or infra commands are available."
    )
    parser.add_argument(
        "--log-level", "--ll", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="WARNING"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Shown for completeness; returns enterprise-only message
    subparsers.add_parser("init-elasticsearch", help="Initialise indices (Enterprise only)")
    subparsers.add_parser("delete-elasticsearch", help="Delete indices (Enterprise only)")

    # Data loading (Enterprise only)
    load_data_parser = subparsers.add_parser("load-data", help="Load regulatory data (Enterprise only)")
    load_data_parser.add_argument(
        "source",
        choices=[
            "handbook",
            "policy-documents",
            "consultation-papers",
            "firms-register",
            "enforcement-notices",
        ],
        help="The data source to load (Enterprise only).",
    )
    load_data_parser.add_argument("--from-date", required=False)
    load_data_parser.add_argument("--to-date", required=False)

    # Serve (Community edition exposes only stub MCP endpoints)
    serve_parser = subparsers.add_parser("serve", help="Run stub MCP server (Enterprise endpoints disabled)")
    serve_parser.add_argument("--no-reload", dest="reload", action="store_false")
    serve_parser.set_defaults(reload=True)

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    configure_logging(level=args.log_level)

    if args.command in {"init-elasticsearch", "delete-elasticsearch", "load-data"}:
        sys.exit(_enterprise_only(args.command))

    if args.command == "serve":
        # Do not import uvicorn/fastapi or start a server in community edition
        sys.exit(_enterprise_only("serve"))

    # Fallback
    sys.exit(1)


if __name__ == "__main__":
    main()
