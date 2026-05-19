import argparse
import json
import logging
import logging.config
import os

from label_studio_ml.api import init_app

from model import GroundingDinoPersonGuitar


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "[%(asctime)s] [%(levelname)s] "
                "[%(name)s::%(funcName)s::%(lineno)d] %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": LOG_LEVEL,
                "stream": "ext://sys.stdout",
                "formatter": "standard",
            }
        },
        "root": {
            "level": LOG_LEVEL,
            "handlers": ["console"],
            "propagate": True,
        },
    }
)


DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def get_kwargs_from_config(config_path: str = DEFAULT_CONFIG_PATH):
    if not os.path.exists(config_path):
        return {}
    with open(config_path) as f:
        config = json.load(f)
    if not isinstance(config, dict):
        raise ValueError("config.json must contain a JSON object.")
    return config


def parse_extra_kwargs(raw_pairs):
    def is_float(value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False

    parsed = {}
    for key, value in raw_pairs or []:
        if value.isdigit():
            parsed[key] = int(value)
        elif value.lower() == "true":
            parsed[key] = True
        elif value.lower() == "false":
            parsed[key] = False
        elif is_float(value):
            parsed[key] = float(value)
        else:
            parsed[key] = value
    return parsed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grounding DINO Label Studio backend")
    parser.add_argument("-p", "--port", type=int, default=9090, help="Server port")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument(
        "--kwargs",
        "--with",
        dest="kwargs",
        metavar="KEY=VAL",
        nargs="+",
        type=lambda kv: kv.split("="),
        help="Additional model initialization kwargs",
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Debug mode")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate backend instance before launching the server",
    )
    parser.add_argument(
        "--basic-auth-user",
        default=os.environ.get("ML_SERVER_BASIC_AUTH_USER"),
        help="Basic auth user",
    )
    parser.add_argument(
        "--basic-auth-pass",
        default=os.environ.get("ML_SERVER_BASIC_AUTH_PASS"),
        help="Basic auth password",
    )
    args = parser.parse_args()

    kwargs = get_kwargs_from_config()
    kwargs.update(parse_extra_kwargs(args.kwargs))

    if args.check:
        GroundingDinoPersonGuitar(**kwargs)
        raise SystemExit(0)

    app = init_app(
        model_class=GroundingDinoPersonGuitar,
        basic_auth_user=args.basic_auth_user,
        basic_auth_pass=args.basic_auth_pass,
    )
    app.run(host=args.host, port=args.port, debug=args.debug)
else:
    app = init_app(model_class=GroundingDinoPersonGuitar)
