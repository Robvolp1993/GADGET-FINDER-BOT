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

# Configurazione completa del sistema di logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_activity.log', mode='a', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Stato globale del bot
bot_active_status = True

# Database completo delle offerte
PRODUCT_OFFERS = {
    "electronics": [
        {
            "name": "Echo Buds (Latest model) | Wireless earbuds with Alexa",
            "price": "€119.99",
            "original_price": "€139.99",
            "url": "https://www.amazon.it/echo-buds",
            "image": "https://m.media-amazon.com/images/I/414iLzSlgXL._AC_SX679_.jpg"
        }
    ],
    # Altre categorie...
}

SPECIAL_OFFERS = [
    {
        "name": "Echo Dot (Latest model)",
        "description": "Smart speaker with Alexa",
        "url": "https://www.amazon.it/echo-dot",
        "image": "https://m.media-amazon.com/images/I/61PtYUvk6VL._AC_SX679_.jpg"
    }
]

async def send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce il messaggio di benvenuto iniziale"""
    welcome_keyboard = [
        [InlineKeyboardButton("🚀 Start Bot", callback_data="start_bot")]
    ]
    await update.message.reply_text(
        text="🛍️ *Welcome to Gadget Finder Bot!* 🛍️\nDiscover the best Amazon deals!",
        reply_markup=InlineKeyboardMarkup(welcome_keyboard),
        parse_mode="Markdown"
    )

async def handle_bot_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce l'avvio del bot dopo la pressione del pulsante"""
    user_query = update.callback_query
    await user_query.answer()
    main_menu_keyboard = [
        [InlineKeyboardButton("📦 Special Offers", callback_data="special_offers")],
        [InlineKeyboardButton("🛍️ Product Categories", callback_data="select_category")]
    ]
    await user_query.edit_message_text(
        text="🔍 *What would you like to do?*",
        reply_markup=InlineKeyboardMarkup(main_menu_keyboard),
        parse_mode="Markdown"
    )

async def show_category_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra il menu delle categorie di prodotti"""
    user_query = update.callback_query
    await user_query.answer()
    category_keyboard = [
        [InlineKeyboardButton("📱 Electronics", callback_data="electronics")],
        [InlineKeyboardButton("💻 Computers", callback_data="computers")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    await user_query.edit_message_text(
        text="🛒 *Select a category:*",
        reply_markup=InlineKeyboardMarkup(category_keyboard),
        parse_mode="Markdown"
    )

async def show_category_offers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra le offerte per una categoria specifica"""
    user_query = update.callback_query
    await user_query.answer()
    selected_category = user_query.data
    
    if selected_category not in PRODUCT_OFFERS:
        await user_query.message.reply_text("⚠️ Category not available")
        return
    
    for offer in PRODUCT_OFFERS[selected_category]:
        try:
            await context.bot.send_photo(
                chat_id=user_query.message.chat.id,
                photo=offer["image"],
                caption=f"🏷️ *{offer['name']}*\n💵 {offer['price']} (was {offer['original_price']})\n🔗 [Buy now]({offer['url']})",
                parse_mode="Markdown"
            )
            await asyncio.sleep(1)
        except Exception as error:
            logger.error(f"Error sending offer: {str(error)}")
    
    back_keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
    await context.bot.send_message(
        chat_id=user_query.message.chat.id,
        text="✅ Here are all available offers for this category!",
        reply_markup=InlineKeyboardMarkup(back_keyboard),
        parse_mode="Markdown"
    )

async def maintain_active_status():
    """Mantiene attivo il worker su Render con segnali regolari"""
    global bot_active_status
    while bot_active_status:
        logger.info("Sending activity signal to Render")
        await asyncio.sleep(20)

async def shutdown_procedure(application):
    """Esegue la procedura di spegnimento controllato"""
    global bot_active_status
    bot_active_status = False
    await application.stop()
    await application.updater.stop()
    logger.info("Bot shutdown completed successfully")

async def run_bot_application():
    """Funzione principale per l'esecuzione del bot"""
    try:
        bot_application = ApplicationBuilder().token(TOKEN).build()

        # Registrazione di tutti i gestori di comandi
        bot_application.add_handler(CommandHandler("start", send_welcome_message))
        bot_application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_welcome_message))
        bot_application.add_handler(CallbackQueryHandler(handle_bot_start, pattern="^start_bot$"))
        bot_application.add_handler(CallbackQueryHandler(show_category_menu, pattern="^select_category$"))
        bot_application.add_handler(CallbackQueryHandler(show_category_offers, pattern="^(electronics|computers)$"))
        
        # Avvio parallelo dei servizi
        async with bot_application:
            await bot_application.start()
            await asyncio.gather(
                bot_application.updater.start_polling(),
                maintain_active_status()
            )
            await bot_application.stop()

    except Exception as critical_error:
        logger.critical(f"CRITICAL ERROR: {str(critical_error)}", exc_info=True)
    finally:
        logger.info("Resource cleanup completed")

def initialize_bot():
    """Punto di ingresso principale per l'inizializzazione del bot"""
    asyncio.run(run_bot_application())

if __name__ == '__main__':
    initialize_bot()
