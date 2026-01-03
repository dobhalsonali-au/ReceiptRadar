# ReceiptRadar

At the start of 2026, one of my New Year resolutions was simple:
**keep track of where my money actually goes.**

Between income, day-to-day expenses, and last minute shopping spree, budgeting always felt more complicated than it needed to be. I wanted something lightweight, local, and honest which means no apps, no logins, no subscriptions.

So I built **ReceiptRadar**.


## The Idea

ReceiptRadar is a **Python-based CLI expense tracker** that helps me:
- log daily expenses as they happen  
- review spending summaries (optionally by month)  
- import bank statements from CSV files  
- stay aware of my budget without overengineering the process  

It’s intentionally simple. If it runs in a terminal and tells me the truth about my spending, it’s doing its job.


## What It Can Do
- Add an expense (amount, category, date, note)
- View total spending and summaries
- Filter summaries by month
- Import transactions from a bank CSV file
- Store everything locally in a readable format



## Tech Stack
- Python 3.x  
- Standard Library only (`csv`, `datetime`, `pathlib`, etc.)

No external dependencies. No magic. Just Python.



## How to Run

### Clone the repo
```bash
git clone https://github.com/dobhalsonali-au/ReceiptRadar.git
cd ReceiptRadar
