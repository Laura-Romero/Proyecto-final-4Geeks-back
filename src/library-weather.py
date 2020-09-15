from pyowm.owm import OWM
from pyowm.utils.config import get_config_from
config_dict = get_config_from('/path/to/configfile.json')  # This utility comes in handy
owm = OWM('your-free-api-key', config_dict)

data = {
        "api_key": "4cd5539f8e0617ff4cc0a570dd24742a",
        "subscription_type": "Free",
        "language": "ru",
        "connection": {
            "use_ssl": True,
            "verify_ssl_certs": True,
            "timeout_secs": 1
        }
    }