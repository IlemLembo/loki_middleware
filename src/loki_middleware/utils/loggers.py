import json
import logging
import os

from colorama import Fore
from dict_field_redacter import DictFieldRedacter

from .handlers import console_handler, loki_handler


class ConsoleLogger:
    def __init__(self, name="ConsoleLogger"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)

    def info(self, message):
        """Log un message INFO"""
        try:
            self.logger.info(f"{Fore.GREEN}{message}{Fore.RESET}")
        except Exception as e:  # noqa: BLE001
            print(f"{Fore.GREEN}Erreur lors de la journalisation INFO: {e}{Fore.RESET}")

    def error(self, message):
        """Log un message ERROR"""
        try:
            self.logger.error(f"{Fore.RED}{message}{Fore.RESET}")
        except Exception as e:  # noqa: BLE001
            print(f"{Fore.RED}Erreur lors de la journalisation ERROR: {e}{Fore.RESET}")

    def warning(self, message):
        """Log un message WARNING"""
        try:
            self.logger.warning(f"{Fore.YELLOW}{message}{Fore.RESET}")
        except Exception as e:  # noqa: BLE001
            print(
                f"{Fore.YELLOW}Erreur lors de la journalisation WARNING: {e}{Fore.RESET}"
            )


class LokiLogger:
    """Configure et gère les logs Loki de manière simple"""

    console_logger = ConsoleLogger("ConsoleLogger")

    def check_health(self):
        """
        Verifier si les variables d'environnement nécessaires sont présentes pour Loki, et que Loki est accessible,
        Pour ider les utilisateurs à mieux debugger les problèmes de configuration.
        """
        loki_url = os.getenv("LOKI_URL")
        if not loki_url:
            self.console_logger.warning(
                f"⚠️  {Fore.RED}LOKI_URL n'est pas défini. Les logs ne seront pas envoyés à Loki.{Fore.RESET}"
            )
            return False

        # Optionnel : Vérifier que Loki est accessible
        try:
            import requests

            # On fait une requete simple pour vérifier que Loki répond. Pas forcément une reponse 200
            response = requests.get(loki_url, timeout=2)
            if (
                response.status_code < 500
            ):  # Loki répond, même si c'est une erreur de requete
                self.console_logger.info(
                    f"✅ {Fore.GREEN}Loki est accessible et prêt à recevoir les logs.{Fore.RESET}"
                )
                return True
            else:
                self.console_logger.warning(
                    f"⚠️  {Fore.RED}Loki est inaccessible (status code: {response.status_code}). Les logs ne seront pas envoyés.{Fore.RESET}"
                )
                return False
        except Exception as e:  # noqa: BLE001
            self.console_logger.error(
                f"⚠️  {Fore.RED}Erreur lors de la connexion à Loki: {e}. Les logs ne seront pas envoyés.{Fore.RESET}"
            )
            return False

    def __init__(self, name="app_logger"):
        """
        Initialise le logger Loki

        Args:
            name: Nom du logger (par défaut "app_logger")
        """
        # Créer le logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.redact = True
        self.sensitive_fields = (
            os.getenv("LOKI_SENSITIVE_FIELDS", "").split(",") if self.redact else []
        )
        self.mask_value = os.getenv("LOKI_MASK_VALUE", "****************")

        # Controler la santé de Loki avant d'ajouter le handler
        if self.check_health():
            self.logger.addHandler(loki_handler)
        else:
            self.console_logger.warning(
                f"⚠️  {Fore.YELLOW}Le handler Loki n'a pas été ajouté en raison de problèmes de santé. Les logs ne seront pas envoyés à Loki.{Fore.RESET}"
            )

        # self.logger.addHandler(self.console_handler)

    def redact_sensitive_info(self, message):
        if not isinstance(message, dict):
            try:
                message = json.loads(message)
            except json.JSONDecodeError as e:
                self.console_logger.error(
                    f"{Fore.RED}Erreur lors de la conversion du message en dict: {e}{Fore.RESET}"
                )
                return message  # Si on ne peut pas convertir, retourner le message original
        redactor = DictFieldRedacter(self.sensitive_fields, maskWith=self.mask_value)
        message = redactor.sanitize(message)
        return json.dumps(message)

    def info(self, message):
        """Log un message INFO"""
        try:
            if self.redact:
                message = self.redact_sensitive_info(message)
            self.logger.info(message)
        except Exception as e:  # noqa: BLE001
            self.console_logger.error(
                f"{Fore.RED}Erreur lors de la journalisation INFO: {e}{Fore.RESET}"
            )

    def error(self, message):
        """Log un message ERROR"""
        try:
            if self.redact:
                message = self.redact_sensitive_info(message)
            self.logger.error(message)
        except Exception as e:  # noqa: BLE001
            self.console_logger.error(
                f"{Fore.RED}Erreur lors de la journalisation ERROR: {e}{Fore.RESET}"
            )

    def warning(self, message):
        """Log un message WARNING"""
        try:
            if self.redact:
                message = self.redact_sensitive_info(message)
            self.logger.warning(message)
        except Exception as e:  # noqa: BLE001
            self.console_logger.error(
                f"{Fore.RED}Erreur lors de la journalisation WARNING: {e}{Fore.RESET}"
            )
