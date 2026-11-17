import os
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

# Configuração dos logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    usuario = update.effective_user

    await update.message.reply_text(
        f"Olá, {usuario.first_name}!\n\n"
        "Bem-vindo ao sistema de solicitações.\n\n"
        "Comandos disponíveis:\n"
        "/nova - Nova solicitação\n"
        "/listar - Listar atividades\n"
        "/ajuda - Ajuda"
    )


async def ajuda(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "Sistema de gerenciamento de atividades.\n\n"
        "Utilize /nova para cadastrar uma solicitação."
    )


async def nova(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "Vamos cadastrar uma nova solicitação!\n\n"
        "Por enquanto, essa funcionalidade está em desenvolvimento."
    )


async def listar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "A consulta de atividades será implementada na próxima etapa."
    )


def main():

    if not TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN não configurado!"
        )

    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("ajuda", ajuda)
    )

    application.add_handler(
        CommandHandler("nova", nova)
    )

    application.add_handler(
        CommandHandler("listar", listar)
    )

    logger.info("Bot Telegram iniciado!")

    application.run_polling()


if __name__ == "__main__":
    main()