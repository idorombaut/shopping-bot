import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load token from file
# with open("token.txt", "r") as f:
#     TOKEN = f.read().strip()

# In-memory shopping list (per bot, shared for all users)
shopping_list = []

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
    if not context.args:
        await update.message.reply_text("⚠️ Please specify an item to add.")
        return

    item = " ".join(context.args)
    shopping_list.append(item)
    await update.message.reply_text(f"✅ Added '{item}' to the list.")

# /list command
async def view_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not shopping_list:
        await update.message.reply_text("🛒 Your shopping list is empty.")
    else:
        items = "\n".join([f"{i+1}. {item}" for i, item in enumerate(shopping_list)])
        await update.message.reply_text(f"📝 **Your Shopping List:**\n{items}", parse_mode="Markdown")

# /remove command
async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Please specify an item to remove.")
        return

    item = " ".join(context.args)
    if item in shopping_list:
        shopping_list.remove(item)
        await update.message.reply_text(f"🗑️ Removed '{item}' from the list.")
    else:
        await update.message.reply_text(f"❌ '{item}' is not in the list.")

# /clear command
async def clear_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shopping_list.clear()
    await update.message.reply_text("🧹 Shopping list cleared.")

# Main function
def main():
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
