import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load token from file
# with open("token.txt", "r") as f:
#     TOKEN = f.read().strip()

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
            # convert keys back to int (JSON keys are strings)
            shopping_lists = {int(k): v for k, v in shopping_lists.items()}
    except FileNotFoundError:
        shopping_lists = {}

# Save shopping lists to file
def save_lists():
    with open(FILE, "w") as f:
        json.dump(shopping_lists, f)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛒 Welcome to the Shopping List Bot!\n"
        "Use /add <item> to add an item\n"
        "Use /list to view items\n"
        "Use /remove <item> to delete an item\n"
        "Use /clear to empty the list"
    )

# /add command
async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("⚠️ Please specify an item to add.")
        return

    item = " ".join(context.args)
    if user_id not in shopping_lists:
        shopping_lists[user_id] = []
    shopping_lists[user_id].append(item)
    save_lists()  # save after change
    await update.message.reply_text(f"✅ Added '{item}' to your list.")

# /list command
async def view_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in shopping_lists or not shopping_lists[user_id]:
        await update.message.reply_text("🛒 Your shopping list is empty.")
        return

    items = "\n".join([f"{i+1}. {item}" for i, item in enumerate(shopping_lists[user_id])])
    await update.message.reply_text(f"📝 **Your Shopping List:**\n{items}", parse_mode="Markdown")

# /remove command
async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("⚠️ Please specify an item to remove.")
        return

    if user_id not in shopping_lists:
        shopping_lists[user_id] = []

    item = " ".join(context.args)
    if item in shopping_lists[user_id]:
        shopping_lists[user_id].remove(item)
        save_lists()
        await update.message.reply_text(f"🗑️ Removed '{item}' from your list.")
    else:
        await update.message.reply_text(f"❌ '{item}' is not in your list.")

# /clear command
async def clear_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    shopping_lists[user_id] = []
    save_lists()
    await update.message.reply_text("🧹 Your shopping list has been cleared.")

# Main function
def main():
    load_lists()  # load saved shopping lists at startup
    TOKEN = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()   

    # app = ApplicationBuilder().token(TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_item))
    app.add_handler(CommandHandler("list", view_list))
    app.add_handler(CommandHandler("remove", remove_item))
    app.add_handler(CommandHandler("clear", clear_list))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
