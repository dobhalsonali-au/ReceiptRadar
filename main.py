from datetime import date, datetime
import csv
from pathlib import Path


FILE_PATH = "ReceiptRadar/Data/expenses.csv"
BUDGETS_PATH = "ReceiptRadar/Data/budgets.csv"


CATEGORY_RULES = {
    "Transport": ["uber", "ola", "ptv", "myki", "tram", "train", "bus", "taxi"],
    "Groceries": ["woolworths", "coles", "aldi", "iga", "grocery", "supermarket"],
    "Food": ["cafe", "coffee", "restaurant", "mcdonald", "kfc", "dominos", "subway"],
    "Bills": ["optus", "telstra", "electricity", "gas", "water", "internet", "bill"],
    "Shopping": ["kmart", "target", "amazon", "ebay", "shein", "zara", "h&m"],
    "Health": ["chemist", "pharmacy", "gp", "doctor", "hospital"],
}


def ensure_header():
    try:
        with open(FILE_PATH, "r") as f:
            first = f.readline().strip().lower()
            if first == "date,name,type,category,amount":
                return
    except FileNotFoundError:
        pass

    # If file doesn't exist, create with new header
    try:
        with open(FILE_PATH, "x") as f:
            f.write("date,name,type,category,amount\n")
    except FileExistsError:
        pass



def guess_category(description: str) -> str:
    text = description.lower()

    for category, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw in text:
                return category

    return "Other"


def add_expense():
    ensure_header()

    name = input("Your name: ").strip()
    description = input("What was it? (e.g., 'Uber to work' or 'Salary'): ").strip()
    amount = float(input("Amount: $"))

    tx_type = input("Type (1=Expense, 2=Income): ").strip()
    if tx_type == "2":
        tx_type = "INCOME"
        category = "Income"
    else:
        tx_type = "EXPENSE"
        guessed = guess_category(description)
        print(f"I think this expense is: {guessed}")
        category = input(f"Press Enter to accept '{guessed}' or type a new category: ").strip()
        category = guessed if not category else category.strip().capitalize()

    use_today = input("Use today's date? (y/n): ").strip().lower()
    if use_today == "y":
        expense_date = date.today().isoformat()
    else:
        expense_date = input("Enter date (YYYY-MM-DD): ").strip()
        datetime.strptime(expense_date, "%Y-%m-%d")

    with open(FILE_PATH, "a") as file:
        file.write(f"{expense_date},{name},{tx_type},{category},{amount}\n")

    print("Saved!\n")




def view_summary():
    try:
        with open(FILE_PATH, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        print("No expenses yet. Add or import first.\n")
        return

    if not lines:
        print("File is empty. Add or import first.\n")
        return

    month_filter = input("Filter by month? Enter YYYY-MM (or press Enter for all): ").strip()

    income_total = 0.0
    expense_total = 0.0
    category_totals = {}
    transactions = []  # (date, type, category, amount)

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Skip header if already present
        if line.lower() == "date,name,type,category,amount":
            continue

        parts = line.split(",")
        if len(parts) != 5:
            continue

        expense_date, name, tx_type, category, amount = parts

        # Optional month filter (YYYY-MM)
        if month_filter and not expense_date.startswith(month_filter):
            continue

        try:
            amount = float(amount)
        except ValueError:
            continue

        tx_type = tx_type.strip().upper()
        category = category.strip()

        if tx_type == "INCOME":
            income_total += amount
        else:
            expense_total += amount
            category_totals[category] = category_totals.get(category, 0) + amount

        transactions.append((expense_date, tx_type, category, amount))

    print("\n--- Summary ---")
    if month_filter:
        print("Month:", month_filter)

    print("Income:  $", round(income_total, 2))
    print("Expenses:$", round(expense_total, 2))
    print("Net:     $", round(income_total - expense_total, 2))

    print("\nSpending by category:")
    for category, amt in category_totals.items():
        print(category, "→ $", round(amt, 2))

    # --- Budget Mode ---
    budgets = load_budgets()
    if budgets:
        print("\n--- Budgets ---")
        for category, spent in category_totals.items():
            if category in budgets:
                limit = budgets[category]
                remaining = limit - spent
                percent = (spent / limit) * 100 if limit > 0 else 0

                status = ""
                if percent >= 100:
                    status = "OOPS!!! OVER budget"
                elif percent >= 80:
                    status = "Welll!!! Near budget"

                print(
                    f"{category}: spent ${round(spent, 2)} / ${round(limit, 2)} "
                    f"({round(percent, 1)}%) | remaining ${round(remaining, 2)} {status}"
                )

    # Top 5 biggest EXPENSE transactions
    expense_transactions = [t for t in transactions if t[1] != "INCOME"]
    top5 = sorted(expense_transactions, key=lambda x: x[3], reverse=True)[:5]

    print("\nTop 5 expenses:")
    for d, ttype, c, a in top5:
        print(f"{d} | {c} | ${round(a, 2)}")

    export = input("\nExport this summary to a report file? (y/n): ").strip().lower()
    if export == "y":
        report_name = f"report_{month_filter if month_filter else 'ALL'}.txt"
        report_path = f"ReceiptRadar/Reports/{report_name}"

        with open(report_path, "w") as r:
            r.write("ReceiptRadar Report\n")
            r.write("-------------------\n")
            r.write(f"Filter: {month_filter if month_filter else 'ALL'}\n")
            r.write(f"Income:  ${round(income_total, 2)}\n")
            r.write(f"Expenses:${round(expense_total, 2)}\n")
            r.write(f"Net:     ${round(income_total - expense_total, 2)}\n\n")

            r.write("Spending by category:\n")
            for category, amt in category_totals.items():
                r.write(f"- {category}: ${round(amt, 2)}\n")

            # Include budgets in report
            if budgets:
                r.write("\nBudgets:\n")
                for category, spent in category_totals.items():
                    if category in budgets:
                        limit = budgets[category]
                        remaining = limit - spent
                        percent = (spent / limit) * 100 if limit > 0 else 0
                        status = "OVER" if percent >= 100 else ("NEAR" if percent >= 80 else "OK")
                        r.write(
                            f"- {category}: spent ${round(spent, 2)} / ${round(limit, 2)} "
                            f"({round(percent, 1)}%) | remaining ${round(remaining, 2)} [{status}]\n"
                        )

            r.write("\nTop 5 expenses:\n")
            for d, ttype, c, a in top5:
                r.write(f"- {d} | {c} | ${round(a, 2)}\n")

        print(f" Exported: {report_path}\n")
    else:
        print()



def load_existing_keys():
    keys = set()
    try:
        with open(FILE_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.lower() == "date,name,type,category,amount":
                    continue

                parts = line.split(",")
                if len(parts) != 5:
                    continue

                d, n, t, c, a = parts
                keys.add(f"{d}|{n}|{t}|{c}|{a}")
    except FileNotFoundError:
        pass

    return keys



def import_bank_csv():
    ensure_header()

    existing_keys = load_existing_keys()

    csv_path = input("Enter bank CSV path (e.g., D:\\Downloads\\bank.csv): ").strip().strip('"')
    if not csv_path:
        print("No path provided.\n")
        return

    path = Path(csv_path)
    if not path.exists():
        print("File not found. Check the path.\n")
        return

    name = input("Your name (used for imported rows): ").strip()

    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("Couldn't read headers from that CSV.\n")
            return

        headers = reader.fieldnames
        print("\nI found these columns:")
        for h in headers:
            print("-", h)

        date_col = input("\nWhich column is DATE? (type exactly): ").strip()
        desc_col = input("Which column is DESCRIPTION/MERCHANT? (type exactly): ").strip()
        amt_col = input("Which column is AMOUNT? (type exactly): ").strip()

        if date_col not in headers or desc_col not in headers or amt_col not in headers:
            print("One of those column names didn’t match. Try again.\n")
            return

        imported = 0
        skipped = 0
        duplicates = 0

        with open(FILE_PATH, "a") as out:
            for row in reader:
                raw_date = (row.get(date_col) or "").strip()
                desc = (row.get(desc_col) or "").strip()
                raw_amt = (row.get(amt_col) or "").strip()

                if not raw_date or not raw_amt:
                    skipped += 1
                    continue

                cleaned_amt = raw_amt.replace("$", "").replace(",", "").strip()

                try:
                    signed_amount = float(cleaned_amt)
                except ValueError:
                    skipped += 1
                    continue

                # Type + category
                if signed_amount < 0:
                    tx_type = "EXPENSE"
                    amount = abs(signed_amount)
                    category = guess_category(desc)
                else:
                    tx_type = "INCOME"
                    amount = signed_amount
                    category = "Income"

                # Normalize date
                try:
                    if "/" in raw_date:
                        try:
                            parsed = datetime.strptime(raw_date, "%d/%m/%Y")
                        except ValueError:
                            parsed = datetime.strptime(raw_date, "%m/%d/%Y")
                        expense_date = parsed.date().isoformat()
                    else:
                        parsed = datetime.strptime(raw_date, "%Y-%m-%d")
                        expense_date = parsed.date().isoformat()
                except ValueError:
                    skipped += 1
                    continue

                # Create a unique key for duplicate detection
                key = f"{expense_date}|{name}|{tx_type}|{category}|{amount}"
                if key in existing_keys:
                    duplicates += 1
                    continue

                out.write(f"{expense_date},{name},{tx_type},{category},{amount}\n")
                existing_keys.add(key)
                imported += 1

    print(f"\n Imported {imported} new rows.")
    if duplicates:
        print(f"Skipped {duplicates} duplicates (already imported).")
    if skipped:
        print(f"Skipped {skipped} rows (missing/bad data).")
    print()


def set_budget():
    category = input("Category to budget (e.g., Food): ").strip().capitalize()
    limit = float(input(f"Monthly budget for {category}: $"))

    # load existing budgets
    budgets = {}
    try:
        with open(BUDGETS_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                c, l = line.split(",")
                budgets[c] = float(l)
    except FileNotFoundError:
        pass

    budgets[category] = limit

    with open(BUDGETS_PATH, "w") as f:
        for c, l in budgets.items():
            f.write(f"{c},{l}\n")

    print(f"Budget set: {category} = ${limit}\n")


def load_budgets():
    budgets = {}
    try:
        with open(BUDGETS_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                c, l = line.split(",")
                budgets[c] = float(l)
    except FileNotFoundError:
        pass
    return budgets


def main():
    while True:
        print("ReceiptRadar")
        print("1) Add expense")
        print("2) View summary (optionally by month)")
        print("3) Import bank CSV")
        print("4) Set monthly budget")
        print("5) Exit")


        choice = input("Choose (1/2/3/4/5): ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_summary()
        elif choice == "5":
            print("Bye!")
            break
        elif choice == "3":
            import_bank_csv()
        elif choice == "4":
            set_budget()
        else:
            print("Pick 1, 2, 3, 4, or 5.\n")


main()
