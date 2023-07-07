import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, Updater, CallbackContext, MessageHandler, CommandHandler
import pickle
from datetime import datetime

TOKEN_BOT = "5959208769:AAE4SZjKbYO1MdnMauYxrW5nGocwHnSENYc"
date_file = "Data_File.txt"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

categories_expense = ["Food", "Transportation", "Shopping", "Bills", "Other"]
categories_incomes = ["basic", "Additional", "family"]


def save_data():
    with open(date_file, 'wb') as file:
        pickle.dump(user_data, file)


def load_data():
    try:
        with open(date_file, 'rb') as file:
            if file.read(1):
                file.seek(0)
                return pickle.load(file)
            else:
                return {}
    except FileNotFoundError:
        return {}


user_data = load_data()


async def start(update: Update, context: CallbackContext) -> None:
    logging.info("command run <START>")
    await update.message.reply_text("Welcome to telegram bot\n"
                                    "I manage your income and expenses\n"
                                    "I also keep reports and can send them to you"
                                    "To learn how to manage the bot, type\n"
                                    "/help - list commands")


async def hellp(update: Update, context: CallbackContext) -> None:
    logging.info("command run <HELP>")
    await update.message.reply_text("Welcome\n"
                                    "Commands:\n"
                                    "/help - Help\n"
                                    "/addexpense <category> <amount> - Add an expense\n"
                                    "/addincome <category> <amount> - Add an income\n"
                                    "/expenses - View all expenses\n"
                                    "/incomes - View all incomes\n"
                                    "/removeexpense <expense_id> - Remove an expense\n"
                                    "/removeincome <income_id> - Remove an income\n"
                                    "/categories - View available categories\n"
                                    "/stats <period> - View statistics (day, week, month, year)\n")


async def add_expense(update: Update, context: CallbackContext) -> None:
    logging.info("command run <ADD_EXPENSE>")
    user_id = str(update.message.from_user.id)
    now = datetime.now()
    date = now.strftime("%d-%m-%Y")
    inp_mess = " ".join(context.args).split(" ")
    categ_title = inp_mess[0].strip()
    if len(inp_mess) != 2:
        await update.message.reply_text("Invalid command. Usage: /addexpense <category> <amount>")
        return

    if categ_title not in categories_expense:
        await update.message.reply_text("Invalid category. Use /categories to view available categories.")
        return

    if user_id not in user_data:
        user_data[user_id] = {}

    if "expense" not in user_data[user_id]:
        user_data[user_id]["expense"] = []

    amount = context.args[1]
    save_dat = {"category": categ_title, "amount": amount, "date": date}
    user_data[user_id]["expense"].append(save_dat)
    await update.message.reply_text(f"Expense added - Category: {context.args[0]}  Amount: {context.args[1]} UAH ")
    save_data()
    logging.info("command end <ADD_EXPENSE>")


async def add_incomes(update: Update, context: CallbackContext) -> None:
    logging.info("command run <ADD_INCOMES>")
    user_id = str(update.message.from_user.id)
    now = datetime.now()
    date = now.strftime("%d-%m-%Y")
    inp_mess = " ".join(context.args).split(" ")
    categ_title = inp_mess[0].strip()
    if len(inp_mess) != 2:
        await update.message.reply_text("Invalid command. Usage: /addincomes <category> <amount>")
        return

    if categ_title not in categories_incomes:
        await update.message.reply_text("Invalid category. Use /categories to view available categories.")
        return

    if user_id not in user_data:
        user_data[user_id] = {}

    if "income" not in user_data[user_id]:
        user_data[user_id]["income"] = []

    amount = context.args[1]
    save_dat = {"category": categ_title, "amount": amount, "date": date}
    user_data[user_id]["income"].append(save_dat)
    await update.message.reply_text(f"Incomes added - Category: {context.args[0]}  Amount: {context.args[1]} UAH ")
    save_data()
    logging.info("command end <ADD_INCOMES>")


async def view_expenses(update: Update, context: CallbackContext) -> None:
    logging.info("command run <VIEW_EXPENSES>")
    user_id = str(update.message.from_user.id)
    expenses = user_data.get(user_id, {}).get("expense", [])
    if not expenses:
        await update.message.reply_text("You don't have any expenses.")
        return

    response = "Expenses:\n"
    for i, expense in enumerate(expenses, start=1):
        response += f"{i}. Category: {expense['category']}, Amount: {expense['amount']}, Date: {expense['date']}\n"

    await update.message.reply_text(response)


async def view_incomes(update: Update, context: CallbackContext) -> None:
    logging.info("command run <VIEW_INCOMES>")
    user_id = str(update.message.from_user.id)
    income = user_data.get(user_id, {}).get("income", [])
    if not income:
        await update.message.reply_text("You don't have any expenses.")
        return

    response = "Income:\n"
    for i, income in enumerate(income, start=1):
        response += f"{i}. Category: {income['category']}, Amount: {income['amount']}, Date: {income['date']}\n"

    await update.message.reply_text(response)
    logging.info("command end <VIEW_INCOMES>")


async def view_categories(update: Update, context: CallbackContext) -> None:
    logging.info("command run <VIEW_CATEGORIES>")
    categories_text1 = "Categories incomes:\n\n"
    categories_text2 = "Categorues expenses:\n\n"

    for category in categories_incomes:
        categories_text1 += f"- {category}\n"

    for category in categories_expense:
        categories_text2 += f"- {category}\n"

    await update.message.reply_text(f" {categories_text1} \n\n {categories_text2}")


async def remove_income(update: Update, context: CallbackContext) -> None:
    logging.info("command run <REMOVE_INCOME>")
    user_id = str(update.message.from_user.id)
    if not user_data.get(user_id, 'income'):
        await update.message.reply_text("You don't have any tasks to remove")
        return
    try:
        removed_idx = int(context.args[0]) - 1
        if isinstance(removed_idx, int):
            income = user_data.get(user_id, {}).get("income", [])
            if removed_idx < 0 or removed_idx >= len(income):
                await update.message.reply_text("Invalid index provided")
            else:
                task = income.pop(removed_idx)
                await update.message.reply_text(f"{task} successfully removed")
        else:
            await update.message.reply_text("Invalid index provided")

    except (ValueError, IndexError):
        await update.message.reply_text("You entered an invalid index.")
    save_data()
    logging.info("command end <REMOVE_INCOME>")


async def remove_expense(update: Update, context: CallbackContext) -> None:
    logging.info("command run <REMOVE_EXPENSE>")
    user_id = str(update.message.from_user.id)
    if not user_data.get(user_id, 'expense'):
        await update.message.reply_text("You don't have any tasks to remove")
        return
    try:
        removed_idx = int(context.args[0]) - 1
        if isinstance(removed_idx, int):
            expense = user_data.get(user_id, {}).get("expense", [])
            if removed_idx < 0 or removed_idx >= len(expense):
                await update.message.reply_text("Invalid index provided")
            else:
                task = expense.pop(removed_idx)
                await update.message.reply_text(f"{task} successfully removed")
        else:
            await update.message.reply_text("Invalid index provided")

    except (ValueError, IndexError):
        await update.message.reply_text("You entered an invalid index.")
    save_data()
    logging.info("command end <REMOVE_EXPENSE>")


async def all_remove(update: Update, context: CallbackContext) -> None:
    logging.info("command run <ALL_REMOVE>")
    user_id = str(update.message.from_user.id)
    if not user_data.get(user_id):
        await update.message.reply_text("You don't have any tasks to remove")
        return

    expense = user_data.get(user_id, {})
    expense.clear()
    await update.message.reply_text("successfully removed")

    save_data()
    logging.info("command end <ALL_REMOVE>")


async def stats(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    inp_mess = " ".join(context.args).split(" ")
    from_date_str = inp_mess[0].strip()
    to_date_str = inp_mess[1].strip()

    expenses = []
    incomes = []

    if len(inp_mess) != 2:
        await update.message.reply_text("Invalid command. Usage: /stats <from_date> <to_date>")
        return

    try:
        from_date_obj = datetime.strptime(from_date_str, "%d-%m-%Y").date()
        to_date_obj = datetime.strptime(to_date_str, "%d-%m-%Y").date()
    except ValueError:
        await update.message.reply_text("Invalid date format. Use the format: DD-MM-YYYY")
        return

    if user_id in user_data:
        user_expenses = user_data[user_id].get("expense", [])
        user_incomes = user_data[user_id].get("income", [])

        for expense in user_expenses:
            expense_date = datetime.strptime(expense["date"], "%d-%m-%Y").date()
            if from_date_obj <= expense_date <= to_date_obj:
                expenses.append(expense)

        for income in user_incomes:
            income_date = datetime.strptime(income["date"], "%d-%m-%Y").date()
            if from_date_obj <= income_date <= to_date_obj:
                incomes.append(income)

    response = f"Expenses from {from_date_str} to {to_date_str}:\n"
    for i, expense in enumerate(expenses, start=1):
        response += f"{i}. Category: {expense['category']}, Amount: {expense['amount']}, Date: {expense['date']}\n"

    response += f"\nIncomes from {from_date_str} to {to_date_str}:\n"
    for i, income in enumerate(incomes, start=1):
        response += f"{i}. Category: {income['category']}, Amount: {income['amount']}, Date: {income['date']}\n"

    await update.message.reply_text(response)


def run():
    app = ApplicationBuilder().token(TOKEN_BOT).build()
    logging.info("Code RUN")
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", hellp))
    app.add_handler(CommandHandler("addincome", add_incomes))
    app.add_handler(CommandHandler("addexpense", add_expense))
    app.add_handler(CommandHandler("incomes", view_incomes))
    app.add_handler(CommandHandler("expenses", view_expenses))
    app.add_handler(CommandHandler("categories", view_categories))
    app.add_handler(CommandHandler("removeincome", remove_income))
    app.add_handler(CommandHandler("removeexpense", remove_expense))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("allremove", all_remove))

    app.run_polling()


if __name__ == "__main__":
    run()

