import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, CallbackQueryHandler, CallbackContext, Filters
from config import TOKEN

# Configurazione del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database completo delle offerte organizzate per categorie
OFFERTE = {
    "elettronica": [
        {
            "nome": "Echo Buds (Ultimo modello) | Auricolari wireless con Alexa, cuffiette Bluetooth con cancellazione attiva del rumore, microfono integrato, IPX4 Impermeabili | Nero",
            "prezzo": "€119,99",
            "prezzo_originale": "€139,99",
            "url": "https://www.amazon.it/echo-buds-2a-generazione/dp/B085WV7HJR/ref=zg_bs_g_electronics_d_sccl_4/260-4553846-7984432?th=1",
            "immagine": "https://m.media-amazon.com/images/I/414iLzSlgXL._AC_SX679_.jpg"
        },
        {
            "nome": "Fire TV Stick 4K Max",
            "prezzo": "€26,99",
            "prezzo_originale": "€44,99",
            "url": "https://www.amazon.it/fire-tv-stick-hd/dp/B0CQMWQDH4/ref=zg_bs_g_electronics_d_sccl_2/260-4553846-7984432?psc=1",
            "immagine": "https://m.media-amazon.com/images/I/51B45gaTgjL._AC_SY300_SX300_.jpg"
        }
    ],
    "informatica": [
        {
            "nome": "SanDisk 128GB Ultra scheda microSDXC + adattatore SD fino a 140 MB/s con prestazioni app A1 UHS-I Class 10 U1",
            "prezzo": "€14,29",
            "prezzo_originale": "€33,43",
            "url": "https://www.amazon.it/SanDisk-microSDXC-adattatore-prestazioni-dellapp/dp/B0B7NTY2S6/ref=zg_bs_g_pc_d_sccl_1/260-4553846-7984432?th=1",
            "immagine": "https://m.media-amazon.com/images/I/71IEQv81sML._AC_SX679_.jpg"
        },
        {
            "nome": "INIU Cavo USB Type-C, Cavo USB A a USB C 3,1A Ricarica Rapida [3Pezzi/0,5+2+2m] Lega Intrecciato in Nylon QC 3,0 Cavo Tipo C per iPhone 16 15 Samsung S22 Xiaomi Huawei Pixel OnePlus Realme ECC",
            "prezzo": "€9,48",
            "prezzo_originale": "€9,99",
            "url": "https://www.amazon.it/INIU-Pezzi%EF%BC%9A0-5-Ricarica-Intrecciato-compatibili/dp/B08J7PQGD7/ref=zg_bs_g_pc_d_sccl_4/260-4553846-7984432?th=1",
            "immagine": "https://m.media-amazon.com/images/I/71Iqt+9lK5L._AC_SX522_.jpg"
        }
    ],
    "casa": [
        {
            "nome": "Nespresso Inissia EN80.B, Macchina da caffè di De'Longhi, Sistema Capsule Nespresso, Serbatoio acqua 0.7L, Nero",
            "prezzo": "€84,99",
            "prezzo_originale": "€104,00",
            "url": "https://www.amazon.it/DeLonghi-Nespresso-Inissia-Macchina-Espresso/dp/B00G5YOVZA/ref=zg_bs_c_kitchen_d_sccl_4/260-4553846-7984432?pd_rd_w=TcRe5&content-id=amzn1.sym.b44bfea3-b155-4350-b7d1-0e6dd1ddb8af&pf_rd_p=b44bfea3-b155-4350-b7d1-0e6dd1ddb8af&pf_rd_r=CNAHZS2FCV5QX3E3EBPC&pd_rd_wg=zISXd&pd_rd_r=1695db7f-9820-4a66-a5e4-ab0c183a6517&pd_rd_i=B00G5YOVZA&th=1",
            "immagine": "https://m.media-amazon.com/images/I/61f4U34vuyL._AC_SY879_.jpg"
        },
        {
            "nome": "Amazon Basics Filtri per acqua, confezione da 12, adatto e compatibile con tutte le caraffe BRITA, incluse le caraffe PerfectFit e Amazon Basic",
            "prezzo": "€30,58",
            "prezzo_originale": "€33,99",
            "url": "https://www.amazon.it/Amazon-Basics-Cartuccia-filtrante-acqua/dp/B084H8YHW8?th=1",
            "immagine": "https://m.media-amazon.com/images/I/71yBxoWEeVL._AC_SX679_.jpg"
        }
    ],
    "giochi": [
        {
            "nome": "Xbox Game Pass Ultimate - 1 Mese Abbonamento – Xbox / Windows PC / Cloud - Download Code",
            "prezzo": "€17,99",
            "prezzo_originale": "€20,00",
            "url": "https://www.amazon.it/Abbonamento-Xbox-Game-Pass-Ultimate/dp/B07SBBGW3T/ref=zg_bs_g_13900044031_d_sccl_1/260-4553846-7984432?psc=1",
            "immagine": "https://m.media-amazon.com/images/I/719la27-8lL._AC_SX679_.jpg"
        },
        {
            "nome": "The Legend of Zelda: Tears of the Kingdom - Videogioco Nintendo - Ed. Italiana - Versione su scheda",
            "prezzo": "€54,90",
            "prezzo_originale": "€60,00",
            "url": "https://www.amazon.it/Legend-Zelda-Videogioco-Nintendo-Italiana/dp/B0BLZMC461/ref=zg_bs_g_13900044031_d_sccl_3/260-4553846-7984432?th=1",
            "immagine": "https://m.media-amazon.com/images/I/81eHh0BNU0L._AC_SY741_.jpg"
        }
    ],
}

# Offerte speciali
OFFERTE_SPECIALI = [
    {
        "nome": "Echo Dot (Ultimo modello)Altoparlante intelligente Wi-Fi e Bluetooth, suono più potente e dinamico, con Alexa | Antracite",
        "descrizione": "Altoparlante intelligente Wi-Fi e Bluetooth, suono più potente e dinamico, con Alexa | Antracite",
        "url": "https://www.amazon.it/echo-dot-2022/dp/B09B8X9RGM?ref=dlx_20719_dg_dcl_B09B8X9RGM_dt_mese3_ea_pi&pf_rd_r=FRPD4TXNK6N1VVM64J2W&pf_rd_p=1b1a98ad-9c63-4bb6-a0d5-7bd38ddb09ea&th=1",
        "immagine": "https://m.media-amazon.com/images/I/61PtYUvk6VL._AC_SX679_.jpg"
    },
    {
        "nome": "ECOVACS DEEBOT T50 PRO OMNI",
        "descrizione": "Robot Aspirapolvere Lavapavimenti, (Migliorato da T30 PRO), 15000 Pa, Spazzola Laterale Estensibile e Lavapavimenti, Aggiunta Automatica Soluzione Detergente, Bianco",
        "url": "https://www.amazon.it/ECOVACS-T50-PRO-OMNI-Aspirapolvere/dp/B0DRJPJLNQ?ref=dlx_20719_dg_dcl_B0DRJPJLNQ_dt_mese3_ea_pi&pf_rd_r=FRPD4TXNK6N1VVM64J2W&pf_rd_p=1b1a98ad-9c63-4bb6-a0d5-7bd38ddb09ea&th=1",
        "immagine": "https://m.media-amazon.com/images/I/617aNfPLnrL._AC_SX679_.jpg"
    }
]

def invia_messaggio_benvenuto(update: Update, context: CallbackContext):
    """Gestisce il messaggio di benvenuto"""
    tastiera = [[InlineKeyboardButton("🚀 Avvia Bot", callback_data="avvia_bot")]]
    update.message.reply_text(
        "🛍️ *Benvenuto in Gadget Finder Bot!* 🛍️\nScopri le migliori offerte Amazon!",
        reply_markup=InlineKeyboardMarkup(tastiera),
        parse_mode="Markdown"
    )

def gestisci_avvio_bot(update: Update, context: CallbackContext):
    """Gestisce l'avvio del bot"""
    query = update.callback_query
    query.answer()
    tastiera = [
        [InlineKeyboardButton("📦 Offerte Speciali", callback_data="offerte_speciali")],
        [InlineKeyboardButton("🛍️ Categorie Prodotti", callback_data="scegli_categoria")]
    ]
    query.edit_message_text(
        "🔍 *Cosa vuoi fare?*",
        reply_markup=InlineKeyboardMarkup(tastiera),
        parse_mode="Markdown"
    )

def mostra_menu_categorie(update: Update, context: CallbackContext):
    """Mostra il menu delle categorie"""
    query = update.callback_query
    query.answer()
    tastiera = [
        [InlineKeyboardButton("📱 Elettronica", callback_data="elettronica")],
        [InlineKeyboardButton("💻 Informatica", callback_data="informatica")],
        [InlineKeyboardButton("🏠 Casa", callback_data="casa")],
        [InlineKeyboardButton("🎮 Giochi", callback_data="giochi")],
        [InlineKeyboardButton("🔙 Torna al Menu", callback_data="torna_al_menu")]
    ]
    query.edit_message_text(
        "🛒 *Seleziona una categoria:*",
        reply_markup=InlineKeyboardMarkup(tastiera),
        parse_mode="Markdown"
    )

def mostra_offerte_categoria(update: Update, context: CallbackContext):
    """Mostra le offerte per una categoria specifica"""
    query = update.callback_query
    categoria = query.data
    query.answer()
    
    if categoria not in OFFERTE:
        query.message.reply_text("⚠️ Categoria non disponibile")
        return
    
    for offerta in OFFERTE[categoria]:
        try:
            context.bot.send_photo(
                chat_id=query.message.chat.id,
                photo=offerta["immagine"],
                caption=f"🏷️ *{offerta['nome']}*\n💵 {offerta['prezzo']} (era {offerta['prezzo_originale']})\n🔗 [Acquista]({offerta['url']})",
                parse_mode="Markdown"
            )
            time.sleep(1)
        except Exception as e:
            logger.error(f"Errore nell'invio dell'offerta: {str(e)}")
    
    # Aggiungiamo il tasto TORNA AL MENU dopo aver mostrato tutte le offerte
    tastiera = [[InlineKeyboardButton("🔙 Torna al Menu", callback_data="torna_al_menu")]]
    context.bot.send_message(
        chat_id=query.message.chat.id,
        text="✅ Ecco tutte le offerte disponibili per questa categoria!",
        reply_markup=InlineKeyboardMarkup(tastiera),
        parse_mode="Markdown"
    )

def mostra_menu_principale(update: Update, context: CallbackContext):
    """Mostra il menu principale"""
    query = update.callback_query
    query.answer()
    tastiera = [
        [InlineKeyboardButton("📦 Offerte Speciali", callback_data="offerte_speciali")],
        [InlineKeyboardButton("🛍️ Categorie Prodotti", callback_data="scegli_categoria")]
    ]
    query.edit_message_text(
        "🔍 *Menu Principale*",
        reply_markup=InlineKeyboardMarkup(tastiera),
        parse_mode="Markdown"
    )

def mostra_menu_offerte_speciali(update: Update, context: CallbackContext):
    """Mostra le offerte speciali"""
    query = update.callback_query
    query.answer()
    
    if len(OFFERTE_SPECIALI) < 2:
        query.message.reply_text("⚠️ Offerte speciali non disponibili")
        return
    
    for offerta in OFFERTE_SPECIALI[:2]:
        try:
            context.bot.send_photo(
                chat_id=query.message.chat.id,
                photo=offerta["immagine"],
                caption=f"🌟 *{offerta['nome']}*\n{offerta['descrizione']}\n🔗 [Vai all'offerta]({offerta['url']})",
                parse_mode="Markdown"
            )
            time.sleep(1)
        except Exception as e:
            logger.error(f"Errore nell'invio dell'offerta speciale: {str(e)}")
    
    tastiera = [
        [InlineKeyboardButton(OFFERTE_SPECIALI[0]["nome"], url=OFFERTE_SPECIALI[0]["url"])],
        [InlineKeyboardButton(OFFERTE_SPECIALI[1]["nome"], url=OFFERTE_SPECIALI[1]["url"])],
        [InlineKeyboardButton("🔙 Torna al Menu", callback_data="torna_al_menu")]
    ]
    query.message.reply_text(
        "💎 *OFFERTE SPECIALI*",
        reply_markup=InlineKeyboardMarkup(tastiera),
        parse_mode="Markdown"
    )

def main():
    """Avvia il bot"""
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, invia_messaggio_benvenuto))
    dispatcher.add_handler(CallbackQueryHandler(gestisci_avvio_bot, pattern="^avvia_bot$"))
    dispatcher.add_handler(CallbackQueryHandler(mostra_menu_offerte_speciali, pattern="^offerte_speciali$"))
    dispatcher.add_handler(CallbackQueryHandler(mostra_menu_categorie, pattern="^scegli_categoria$"))
    dispatcher.add_handler(CallbackQueryHandler(mostra_offerte_categoria, pattern="^(elettronica|informatica|casa|giochi)$"))
    dispatcher.add_handler(CallbackQueryHandler(mostra_menu_principale, pattern="^torna_al_menu$"))

    print("🤖 Bot avviato correttamente. Premi CTRL+C per fermarlo.")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
