    
from requests import post
import logging
from .handlers import console_handler


def notify_on_telegram(message:str, bot_token:str, chat_id:str):
    """Configure et gère les logs Loki de manière simple"""

    console_logger = logging.getLogger("console_logger")
    console_logger.setLevel(logging.INFO)
    
    console_logger.addHandler(console_handler)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        response = post(url, data=payload, timeout=5)
        return response
    except Exception as e:
        console_logger.error(f"Erreur lors de l'envoi de la notification Telegram: {e}")
        raise