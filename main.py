import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    CommandHandler
)
from config import TOKEN

# Configurazione completa del sistema di registrazione degli eventi
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('registro_bot.log', mode='a', encoding='utf-8')
    ]
)
registratore = logging.getLogger(__name__)

# Variabile per il controllo dello stato di funzionamento
stato_di_funzionamento_del_bot = True

# Database completo delle offerte organizzate per categorie
CATALOGO_OFFERTE = {
    "elettronica": [
        {
            "nome": "Echo Buds (Ultimo modello) | Auricolari wireless con Alexa",
            "prezzo": "€119,99",
            "prezzo_originale": "€139,99",
            "url": "https://www.amazon.it/echo-buds-2a-generazione/dp/B085WV7HJR",
            "immagine": "https://m.media-amazon.com/images/I/414iLzSlgXL._AC_SX679_.jpg"
        }
    ],
    # Altre categorie...
}

OFFERTE_PROMOZIONALI = [
    {
        "nome": "Echo Dot (Ultimo modello)",
        "descrizione": "Altoparlante intelligente Wi-Fi e Bluetooth",
        "url": "https://www.amazon.it/echo-dot-2022/dp/B09B8X9RGM",
        "immagine": "https://m.media-amazon.com/images/I/61PtYUvk6VL._AC_SX679_.jpg"
    }
]

async def inviare_messaggio_di_benvenuto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce l'invio del messaggio iniziale di benvenuto"""
    tastiera_di_benvenuto = [
        [InlineKeyboardButton("🚀 Avvia Bot", callback_data="avvia_bot")]
    ]
    await update.message.reply_text(
        text="🛍️ *Benvenuto in Gadget Finder Bot!* 🛍️\nScopri le migliori offerte Amazon!",
        reply_markup=InlineKeyboardMarkup(tastiera_di_benvenuto),
        parse_mode="Markdown"
    )

async def gestire_avvio_del_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce l'interazione con il pulsante di avvio"""
    richiesta = update.callback_query
    await richiesta.answer()
    tastiera_principale = [
        [InlineKeyboardButton("📦 Offerte Speciali", callback_data="offerte_speciali")],
        [InlineKeyboardButton("🛍️ Categorie Prodotti", callback_data="scegli_categoria")]
    ]
    await richiesta.edit_message_text(
        text="🔍 *Cosa vuoi fare?*",
        reply_markup=InlineKeyboardMarkup(tastiera_principale),
        parse_mode="Markdown"
    )

async def visualizzare_menu_categorie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra l'elenco delle categorie disponibili"""
    richiesta = update.callback_query
    await richiesta.answer()
    tastiera_categorie = [
        [InlineKeyboardButton("📱 Elettronica", callback_data="elettronica")],
        [InlineKeyboardButton("💻 Informatica", callback_data="informatica")],
        [InlineKeyboardButton("🔙 Torna al Menu", callback_data="torna_al_menu")]
    ]
    await richiesta.edit_message_text(
        text="🛒 *Seleziona una categoria:*",
        reply_markup=InlineKeyboardMarkup(tastiera_categorie),
        parse_mode="Markdown"
    )

async def visualizzare_offerte_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra le offerte per la categoria selezionata"""
    richiesta = update.callback_query
    await richiesta.answer()
    categoria_selezionata = richiesta.data
    
    if categoria_selezionata not in CATALOGO_OFFERTE:
        await richiesta.message.reply_text("⚠️ Categoria non disponibile")
        return
    
    for offerta in CATALOGO_OFFERTE[categoria_selezionata]:
        try:
            await context.bot.send_photo(
                chat_id=richiesta.message.chat.id,
                photo=offerta["immagine"],
                caption=f"🏷️ *{offerta['nome']}*\n💵 {offerta['prezzo']} (era {offerta['prezzo_originale']})\n🔗 [Acquista]({offerta['url']})",
                parse_mode="Markdown"
            )
            await asyncio.sleep(1)
        except Exception as errore:
            registratore.error(f"Errore nell'invio dell'offerta: {str(errore)}")
    
    tastiera_indietro = [[InlineKeyboardButton("🔙 Torna al Menu", callback_data="torna_al_menu")]]
    await context.bot.send_message(
        chat_id=richiesta.message.chat.id,
        text="✅ Ecco tutte le offerte disponibili per questa categoria!",
        reply_markup=InlineKeyboardMarkup(tastiera_indietro),
        parse_mode="Markdown"
    )

async def mantenere_attivita():
    """Invia segnali regolari per mantenere attivo il servizio su Render"""
    global stato_di_funzionamento_del_bot
    while stato_di_funzionamento_del_bot:
        registratore.info("Invio segnale di attività a Render")
        await asyncio.sleep(20)

async def procedura_di_arresto(applicazione):
    """Gestisce la chiusura controllata dell'applicazione"""
    global stato_di_funzionamento_del_bot
    stato_di_funzionamento_del_bot = False
    await applicazione.stop()
    await applicazione.updater.stop()
    registratore.info("Applicazione arrestata correttamente")

async def eseguire_applicazione_bot():
    """Funzione principale per l'esecuzione del bot"""
    try:
        applicazione_bot = ApplicationBuilder().token(TOKEN).build()

        # Registrazione completa di tutti i gestori di comandi
        applicazione_bot.add_handler(CommandHandler("start", inviare_messaggio_di_benvenuto))
        applicazione_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, inviare_messaggio_di_benvenuto))
        applicazione_bot.add_handler(CallbackQueryHandler(gestire_avvio_del_bot, pattern="^avvia_bot$"))
        applicazione_bot.add_handler(CallbackQueryHandler(visualizzare_menu_categorie, pattern="^scegli_categoria$"))
        applicazione_bot.add_handler(CallbackQueryHandler(visualizzare_offerte_categoria, pattern="^(elettronica|informatica)$"))

        # Avvio dei servizi in parallelo
        async with applicazione_bot:
            await applicazione_bot.start()
            await asyncio.gather(
                applicazione_bot.updater.start_polling(),
                mantenere_attivita()
            )
            await applicazione_bot.stop()

    except Exception as errore_grave:
        registratore.critical(f"ERRORE GRAVE: {str(errore_grave)}", exc_info=True)
    finally:
        registratore.info("Processo di pulizia completato")

def avviare_bot():
    """Funzione di ingresso principale"""
    asyncio.run(eseguire_applicazione_bot())

if __name__ == '__main__':
    avviare_bot()
