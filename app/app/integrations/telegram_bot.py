import os
import logging
import httpx

from app.services.functions_proc import Prioridades
from telegram import Update
from telegram.ext import (
    Application,
     Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

# Configuração dos logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Configuração de autenticação
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv(
    "FLASK_API_URL",
    "http://python:5000"
)


# Interação com o usuário
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
        "/listar_tudo - Listar atividades\n"
        "/ajuda - Ajudar\n"
        f"{API_URL}/api/tudo, hello"
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

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:

            resposta = await client.get(
                f"{API_URL}/api/tudo"
            )

            resposta.raise_for_status()

            dados = resposta.json()

        if not dados.get("success"):
            await update.message.reply_text(
                "Não foi possível consultar as atividades."
            )
            return

        atividades = dados.get("dados", [])

        if not atividades:
            await update.message.reply_text(
                "Não existem atividades cadastradas."
            )
            return

        mensagem = "📋 ATIVIDADES CADASTRADAS\n\n"

        for atividade in atividades:

            prioridade_num = atividade.get("prioridade")

            prioridade_texto = Prioridades.get(
                prioridade_num,
                "Não informada"
            )

            mensagem += (
                f"🔹 Solicitação #{atividade.get('id', 'N/A')}\n"
                f"Descrição: {atividade.get('subject', 'Não informada')}\n"
                f"Status: {atividade.get('status', 'Não informado')}\n"
                f"Prioridade: {prioridade_texto}\n"
                f"Responsável: {atividade.get('responsavel') or 'Não informado'}\n\n"
            )

        await update.message.reply_text(mensagem)

    except httpx.TimeoutException:

        await update.message.reply_text(
            "A consulta demorou muito. Tente novamente."
        )

    except httpx.HTTPError:

        logger.exception("Erro na comunicação com a API Flask")

        await update.message.reply_text(
            "Não foi possível conectar ao sistema de solicitações."
        )

    except Exception:

        logger.exception("Erro inesperado ao listar atividades")

        await update.message.reply_text(
            "Ocorreu um erro ao consultar as atividades."
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
        CommandHandler("listar_tudo", listar)
    )

    logger.info("Bot Telegram iniciado!")

    application.run_polling()


if __name__ == "__main__":
    main()