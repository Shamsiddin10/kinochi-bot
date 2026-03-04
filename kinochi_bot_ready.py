#!/usr/bin/env python3
"""
🎬 Kinochi Bot — API keysiz, Wikipedia + IMDb scraping
"""

import logging
import random
import re
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes,
)

# ===================== SOZLAMALAR =====================
BOT_TOKEN = "8718045443:AAFHm5pKNPJlw0j6ePMVFnXzN7iXRG7re9g"  # @BotFather dan oling

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ===================== MASHHUR KINOLAR RO'YXATI =====================
POPULAR_MOVIES = [
    {"title": "Inception", "year": "2010", "imdb_id": "tt1375666", "rating": "8.8",
     "genre": "Ilmiy-fantastik, Triller", "director": "Christopher Nolan",
     "plot": "Ong ichiga kirish texnologiyasi yordamida g'oya o'g'irlash bo'yicha mutaxassis Dom Cobb o'z jamoasi bilan eng murakkab missiyani bajaradi.",
     "poster": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg"},
    {"title": "The Dark Knight", "year": "2008", "imdb_id": "tt0468569", "rating": "9.0",
     "genre": "Jangovar, Jinoyat, Drama", "director": "Christopher Nolan",
     "plot": "Batman Gothemni Joker degan anarxistdan himoya qilishi kerak. Joker shaharni tartibsizlikka solmoqchi.",
     "poster": "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg"},
    {"title": "Interstellar", "year": "2014", "imdb_id": "tt0816692", "rating": "8.7",
     "genre": "Sarguzasht, Drama, Ilmiy-fantastik", "director": "Christopher Nolan",
     "plot": "Yer yashash uchun yaroqsiz bo'lib borayotgan paytda, kosmoschilar guruhimiz yangi uy izlab koinotga yo'l oladi.",
     "poster": "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg"},
    {"title": "The Shawshank Redemption", "year": "1994", "imdb_id": "tt0111161", "rating": "9.3",
     "genre": "Drama", "director": "Frank Darabont",
     "plot": "Nohaq qamalgan bank menedjeri Andy Dufresne qamoqxonada umid va do'stlik bilan hayotini davom ettiradi.",
     "poster": "https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_SX300.jpg"},
    {"title": "Forrest Gump", "year": "1994", "imdb_id": "tt0109830", "rating": "8.8",
     "genre": "Drama, Romantik", "director": "Robert Zemeckis",
     "plot": "Past IQ ga ega Forrest Gump o'ziga xos hayotiy yo'lida Amerika tarixining muhim voqealarida ishtirok etadi.",
     "poster": "https://m.media-amazon.com/images/M/MV5BNWIwODRlZTUtY2U3ZS00Yzg1LWJhNzYtMmZiYmEyNmU1NjMzXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_SX300.jpg"},
    {"title": "The Matrix", "year": "1999", "imdb_id": "tt0133093", "rating": "8.7",
     "genre": "Jangovar, Ilmiy-fantastik", "director": "Wachowski Sisters",
     "plot": "Kompyuter xakeri Neo haqiqat aslida sun'iy ekanligini va insonlar mashinalarga qul ekanligini bilib oladi.",
     "poster": "https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVlLTM5YTUtZGNmYWMwMDZiMWE4XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg"},
    {"title": "Pulp Fiction", "year": "1994", "imdb_id": "tt0110912", "rating": "8.9",
     "genre": "Jinoyat, Drama", "director": "Quentin Tarantino",
     "plot": "Los-Angelesdagi jinoyat dunyosidan bir necha o'zaro bog'liq hikoyalar.",
     "poster": "https://m.media-amazon.com/images/M/MV5BNGNhMDIzZTUtNTBlZi00MTRlLWFjM2ItYzViMjE3YzI5MjljXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg"},
    {"title": "Parasite", "year": "2019", "imdb_id": "tt6751668", "rating": "8.5",
     "genre": "Komediya, Drama, Triller", "director": "Bong Joon-ho",
     "plot": "Kambag'al oila boy oila hayotiga asta-sekin kirib boradi. Oscar mukofoti sohibi.",
     "poster": "https://m.media-amazon.com/images/M/MV5BYWZjMjk3ZTItODQ2ZC00NTY5LWE0ZDYtZTI3MjcwN2Q5NTVkXkEyXkFqcGdeQXVyODk4OTc3MTY@._V1_SX300.jpg"},
    {"title": "Gladiator", "year": "2000", "imdb_id": "tt0172495", "rating": "8.5",
     "genre": "Jangovar, Drama", "director": "Ridley Scott",
     "plot": "Rim generali Maximus xoinlik tufayli oilasini yo'qotib, gladiator sifatida qasos izlaydi.",
     "poster": "https://m.media-amazon.com/images/M/MV5BMDliMmNhNDEtODUyOS00MjNlLTgxODEtN2U3NzIxMGVkZTA1XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg"},
    {"title": "Avengers: Endgame", "year": "2019", "imdb_id": "tt4154796", "rating": "8.4",
     "genre": "Jangovar, Sarguzasht, Drama", "director": "Anthony & Joe Russo",
     "plot": "Thanos koinotning yarmini yo'q qilgandan so'ng, Avenjerlar vaziyatni tiklash uchun vaqt sayohati qiladi.",
     "poster": "https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_SX300.jpg"},
    {"title": "The Lion King", "year": "1994", "imdb_id": "tt0110357", "rating": "8.5",
     "genre": "Multfilm, Sarguzasht, Drama", "director": "Roger Allers",
     "plot": "Yosh sher Simba otasining o'limidan keyin qochib ketadi, lekin oxirida o'z taxtini qaytarib oladi.",
     "poster": "https://m.media-amazon.com/images/M/MV5BYTYxNGMyZTYtMjE3MS00MzNjLWFjNmYtMDk3N2FmM2JiM2M1XkEyXkFqcGdeQXVyNjY5NDU4NzI@._V1_SX300.jpg"},
    {"title": "Titanic", "year": "1997", "imdb_id": "tt0120338", "rating": "7.9",
     "genre": "Drama, Romantik", "director": "James Cameron",
     "plot": "1912 yilda cho'kkan Titanik kemachasida turli ijtimoiy tabaqadan kelgan ikki yoshning muhabbat hikoyasi.",
     "poster": "https://m.media-amazon.com/images/M/MV5BMDdmZGU3NDQtY2E5My00ZTliLWIzOTUtMTY4ZGI1YjdiNjk3XkEyXkFqcGdeQXVyNTA4NTY3MjY@._V1_SX300.jpg"},
    {"title": "Avatar", "year": "2009", "imdb_id": "tt0499549", "rating": "7.9",
     "genre": "Jangovar, Sarguzasht, Fantastika", "director": "James Cameron",
     "plot": "Pandora sayyorasida nogironlar aravachasidagi askar mahalliy xalq bilan birlashib, bosqinchilarga qarshi kurashadi.",
     "poster": "https://m.media-amazon.com/images/M/MV5BZDA0OGQxNTItMDZkMC00N2UyLTg3MzMtOTViZjM3ZTgyNWI4XkEyXkFqcGdeQXVyMjUzOTY1NTc@._V1_SX300.jpg"},
    {"title": "Spider-Man: No Way Home", "year": "2021", "imdb_id": "tt10872600", "rating": "8.2",
     "genre": "Jangovar, Sarguzasht, Fantastika", "director": "Jon Watts",
     "plot": "Peter Parker parallel koinotlardan kelgan dushmanlar bilan kurashadi va qiyin qaror qabul qiladi.",
     "poster": "https://m.media-amazon.com/images/M/MV5BZWMyYzFjYTYtNTRjYi00OGExLWE2YzgtOGRmYjAxZTU3NzBiXkEyXkFqcGdeQXVyMzQ0MzA0NTM@._V1_SX300.jpg"},
    {"title": "Joker", "year": "2019", "imdb_id": "tt7286456", "rating": "8.4",
     "genre": "Jinoyat, Drama, Triller", "director": "Todd Phillips",
     "plot": "Artur Fleck — Gothemning unutilgan komediyachisi — qanday qilib Jokerga aylanganining dahshatli hikoyasi.",
     "poster": "https://m.media-amazon.com/images/M/MV5BNGVjNWI4ZGUtNzE0MS00YTJmLWE0ZDctN2ZiYTk2YmI3NTYyXkEyXkFqcGdeQXVyMTkxNjUyNQ@@._V1_SX300.jpg"},
]

TOP_RATED = sorted(POPULAR_MOVIES, key=lambda x: float(x["rating"]), reverse=True)

# ===================== QIDIRISH =====================

def search_local(query: str) -> list:
    """Mahalliy bazadan qidirish"""
    query_lower = query.lower()
    results = []
    for m in POPULAR_MOVIES:
        if query_lower in m["title"].lower():
            results.append(m)
    return results


def search_wikipedia(query: str) -> dict | None:
    """Wikipedia dan kino ma'lumoti olish"""
    try:
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query", "format": "json",
            "list": "search", "srsearch": f"{query} film",
            "srlimit": 3,
        }
        r = requests.get(search_url, params=params, headers=HEADERS, timeout=8)
        data = r.json()
        results = data.get("query", {}).get("search", [])
        if not results:
            return None

        # Birinchi natijani ol
        page_title = results[0]["title"]
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title.replace(' ', '_')}"
        r2 = requests.get(summary_url, headers=HEADERS, timeout=8)
        info = r2.json()

        if info.get("type") == "disambiguation":
            if len(results) > 1:
                page_title = results[1]["title"]
                r2 = requests.get(
                    f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title.replace(' ', '_')}",
                    headers=HEADERS, timeout=8
                )
                info = r2.json()

        extract = info.get("extract", "")
        if len(extract) > 400:
            extract = extract[:400] + "..."

        return {
            "title": info.get("title", query),
            "year": "?",
            "rating": "?",
            "genre": "?",
            "director": "?",
            "plot": extract or "Ma'lumot topilmadi.",
            "poster": info.get("thumbnail", {}).get("source", ""),
            "wiki_url": info.get("content_urls", {}).get("desktop", {}).get("page", ""),
            "imdb_id": "",
        }
    except Exception as e:
        logger.error(f"Wikipedia xato: {e}")
        return None


# ===================== FORMAT =====================

def format_card(m: dict, short=True) -> str:
    rating = m.get("rating", "?")
    try:
        stars = "⭐" * int(float(rating) / 2)
    except Exception:
        stars = ""

    text = (
        f"🎬 *{m['title']}* ({m.get('year','?')})\n"
        f"⭐ Reyting: *{rating}/10* {stars}\n"
        f"🎭 Janr: {m.get('genre','?')}\n"
        f"🎥 Rejissor: {m.get('director','?')}\n\n"
        f"📖 {m.get('plot','')[:300]}{'...' if len(m.get('plot',''))>300 else ''}\n"
    )
    return text


def movie_keyboard(m: dict) -> InlineKeyboardMarkup:
    iid = m.get("imdb_id", "")
    wiki = m.get("wiki_url", "")
    kb = []
    row = []
    if iid:
        row.append(InlineKeyboardButton("🔗 IMDb", url=f"https://www.imdb.com/title/{iid}/"))
    if wiki:
        row.append(InlineKeyboardButton("📖 Wikipedia", url=wiki))
    if row:
        kb.append(row)
    return InlineKeyboardMarkup(kb) if kb else None


async def send_movie(message, m: dict):
    text = format_card(m)
    poster = m.get("poster", "")
    kb = movie_keyboard(m)

    try:
        if poster:
            await message.reply_photo(
                photo=poster, caption=text,
                parse_mode="Markdown", reply_markup=kb
            )
        else:
            await message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    except Exception:
        await message.reply_text(text, parse_mode="Markdown", reply_markup=kb)


# ===================== KOMANDALAR =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    text = (
        f"🎬 Salom, *{u.first_name}*! Kinochi botga xush kelibsiz! 🍿\n\n"
        "Kino nomini yozing — men qidiraman!\n\n"
        "🌟 /popular — Mashhur kinolar\n"
        "🏆 /toprated — Top reytingli\n"
        "🎲 /random — Tasodifiy tavsiya\n"
        "ℹ️ /help — Yordam\n\n"
        "💡 Sinab ko'ring: *Inception* yoki *Joker* yozing!"
    )
    kb = [[
        InlineKeyboardButton("🌟 Mashhur", callback_data="popular"),
        InlineKeyboardButton("🏆 Top", callback_data="toprated"),
    ], [
        InlineKeyboardButton("🎲 Tasodifiy", callback_data="random"),
        InlineKeyboardButton("ℹ️ Yordam", callback_data="help"),
    ]]
    await update.message.reply_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 *Yordam*\n\n"
        "Kino nomini yozing → bot qidiradi\n\n"
        "/popular — Mashhur kinolar\n"
        "/toprated — Top reyting\n"
        "/random — Tasodifiy kino\n\n"
        "💡 Bazada yo'q kino ham qidiriladi (Wikipedia orqali)\n"
        "Inglizcha yozsangiz aniqroq topiladi!",
        parse_mode="Markdown"
    )


async def popular_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movies = POPULAR_MOVIES[:10]
    text = "🌟 *Mashhur kinolar:*\n\n"
    kb = []
    for i, m in enumerate(movies, 1):
        text += f"{i}. *{m['title']}* ({m['year']}) ⭐{m['rating']}\n"
        kb.append([InlineKeyboardButton(f"🎬 {m['title']}", callback_data=f"local_{POPULAR_MOVIES.index(m)}")])
    await update.message.reply_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def toprated_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movies = TOP_RATED[:10]
    text = "🏆 *Top reytingli kinolar:*\n\n"
    kb = []
    for i, m in enumerate(movies, 1):
        text += f"{i}. *{m['title']}* ({m['year']}) ⭐{m['rating']}\n"
        idx = POPULAR_MOVIES.index(m)
        kb.append([InlineKeyboardButton(f"🏆 {m['title']}", callback_data=f"local_{idx}")])
    await update.message.reply_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def random_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = random.choice(POPULAR_MOVIES)
    await send_movie(update.message, m)


# ===================== XABAR HANDLER =====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    await update.message.reply_text(f"🔍 *\"{query}\"* qidirilmoqda...", parse_mode="Markdown")

    # 1. Mahalliy bazadan qidirish
    local = search_local(query)
    if local:
        if len(local) == 1:
            await send_movie(update.message, local[0])
        else:
            text = f"🎬 *\"{query}\"* natijalari:\n\n"
            kb = []
            for m in local[:8]:
                text += f"• *{m['title']}* ({m['year']}) ⭐{m['rating']}\n"
                kb.append([InlineKeyboardButton(
                    f"🎬 {m['title']}", callback_data=f"local_{POPULAR_MOVIES.index(m)}"
                )])
            await update.message.reply_text(
                text, parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(kb)
            )
        return

    # 2. Wikipedia dan qidirish
    await update.message.reply_text("🌐 Wikipedia dan qidirilmoqda...")
    wiki = search_wikipedia(query)
    if wiki:
        await send_movie(update.message, wiki)
    else:
        await update.message.reply_text(
            f"😔 *\"{query}\"* topilmadi.\n\n"
            "💡 Kino nomini inglizcha yozing.\nMasalan: `Inception`, `Avatar`",
            parse_mode="Markdown"
        )


# ===================== CALLBACK =====================

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data

    if d.startswith("local_"):
        idx = int(d.split("_")[1])
        m = POPULAR_MOVIES[idx]
        await send_movie(q.message, m)

    elif d == "popular":
        movies = POPULAR_MOVIES[:10]
        text = "🌟 *Mashhur kinolar:*\n\n"
        kb = []
        for i, m in enumerate(movies, 1):
            text += f"{i}. *{m['title']}* ({m['year']}) ⭐{m['rating']}\n"
            kb.append([InlineKeyboardButton(f"🎬 {m['title']}", callback_data=f"local_{POPULAR_MOVIES.index(m)}")])
        await q.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

    elif d == "toprated":
        movies = TOP_RATED[:10]
        text = "🏆 *Top reytingli kinolar:*\n\n"
        kb = []
        for i, m in enumerate(movies, 1):
            text += f"{i}. *{m['title']}* ({m['year']}) ⭐{m['rating']}\n"
            kb.append([InlineKeyboardButton(f"🏆 {m['title']}", callback_data=f"local_{POPULAR_MOVIES.index(m)}")])
        await q.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

    elif d == "random":
        m = random.choice(POPULAR_MOVIES)
        await send_movie(q.message, m)

    elif d == "help":
        await q.message.reply_text(
            "🎬 Kino nomini yozing → bot qidiradi\n/popular /toprated /random",
            parse_mode="Markdown"
        )


async def error_handler(update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Xato: {context.error}")


# ===================== MAIN =====================

def main():
    print("🎬 Kinochi Bot ishga tushmoqda...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("popular", popular_cmd))
    app.add_handler(CommandHandler("toprated", toprated_cmd))
    app.add_handler(CommandHandler("random", random_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_error_handler(error_handler)
    print("✅ Bot ishga tushdi! Toxtatish: Ctrl+C")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()