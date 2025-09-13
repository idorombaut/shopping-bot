import os
import json
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# TO-DO: Replace JSON storage with a DB for Railway deployment

# Load token from file
with open("config.txt", "r") as f:
    TOKEN = f.read().strip()

# File to store shopping lists
FILE = "shopping_lists.json"

# Dictionary to store each user's shopping list
shopping_lists = {}  # {user_id: [item1, item2, ...]}

# Load shopping lists from file
def load_lists():
    global shopping_lists
    try:
        with open(FILE, "r") as f:
            shopping_lists = json.load(f)
            shopping_lists = {int(k): v for k, v in shopping_lists.items()}
    except FileNotFoundError:
        shopping_lists = {}

# Save shopping lists to file
def save_lists():
    with open(FILE, "w") as f:
        json.dump(shopping_lists, f)

# Main menu keyboard buttons
keyboard = [
    [KeyboardButton("➕ Add Item")],
    [KeyboardButton("📄 View List"), KeyboardButton("🗑 Remove Item")],
    [KeyboardButton("🧹 Clear List")]
]

reply_markup = ReplyKeyboardMarkup(
    keyboard,
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="Choose an action..."
)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛒 Welcome to the Shopping List Bot!\nUse the buttons below to manage your list.",
        reply_markup=reply_markup
    )

# /list command
async def view_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    items = shopping_lists.get(user_id, [])
    if not items:
        await update.message.reply_text("🛒 Your shopping list is empty.", reply_markup=reply_markup)
    else:
        item_text = "\n".join([f"• {item}" for item in items])
        await update.message.reply_text(f"📝 <b>Your Shopping List:</b>\n{item_text}", parse_mode="HTML", reply_markup=reply_markup)

# /clear command
async def clear_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    shopping_lists[user_id] = []
    save_lists()
    await update.message.reply_text("🧹 Your shopping list has been cleared.", reply_markup=reply_markup)

# Generate inline keyboard for removing items
def generate_remove_keyboard(user_id):
    items = shopping_lists.get(user_id, [])
    if not items:
        return None
    buttons = [
        [InlineKeyboardButton(text=item, callback_data=f"remove:{item}")]
        for item in items
    ]
    return InlineKeyboardMarkup(buttons)

# /remove command
async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = generate_remove_keyboard(user_id)
    
    if not keyboard:
        await update.message.reply_text("🛒 Your shopping list is empty.", reply_markup=reply_markup)
        return
    
    await update.message.reply_text("🗑 Select an item to remove:", reply_markup=keyboard)

# Handle inline button clicks
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data.startswith("remove:"):
        item_to_remove = data.split("remove:")[1]
        if item_to_remove in shopping_lists.get(user_id, []):
            shopping_lists[user_id].remove(item_to_remove)
            save_lists()
            # Edit the original message to show removal, remove inline buttons
            await query.edit_message_text(
                text=f"🗑 Removed '{item_to_remove}' from your list.",
                reply_markup=None
            )
        else:
            await query.edit_message_text(
                text=f"❌ '{item_to_remove}' is not in your list.",
                reply_markup=None
            )

# /add command
async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please type the item you want to add:", reply_markup=reply_markup)
    context.user_data["awaiting_add"] = True

# Unified text handler
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Handle main menu buttons
    if text == "➕ Add Item":
        await add_item(update, context)
    elif text == "📄 View List":
        await view_list(update, context)
    elif text == "🗑 Remove Item":
        await remove_item(update, context)
    elif text == "🧹 Clear List":
        await clear_list(update, context)
    # Handle adding new item
    elif context.user_data.get("awaiting_add"):
        if user_id not in shopping_lists:
            shopping_lists[user_id] = []
        shopping_lists[user_id].append(text)
        save_lists()
        context.user_data["awaiting_add"] = False
        await update.message.reply_text(f"✅ Added '{text}' to your list.", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Please use the buttons below.", reply_markup=reply_markup)

# Main function
def main():
    load_lists()
    app = ApplicationBuilder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_item))
    app.add_handler(CommandHandler("list", view_list))
    app.add_handler(CommandHandler("remove", remove_item))
    app.add_handler(CommandHandler("clear", clear_list))

    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    # Inline button handler
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
