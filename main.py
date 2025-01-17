import pandas as pd
import csv
from datetime import datetime
from data_entry import get_amount, get_category, get_date, get_description
import matplotlib.pyplot as plt


class CSV:
    CSV_FILE = "finance_data.csv"
    COLUMNS = ["date", "amount", "category", "description"]
    FORMAT = "%d-%m-%Y"

    @classmethod
    def initialize_csv(cls):
        """Initializes the CSV file with headers if it does not exist, and adds sample data."""
        try:
            df = pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)
            cls.add_sample_data(df)

    @classmethod
    def add_entry(cls, date, amount, category, description):
        """Adds a new entry to the CSV file."""
        new_entry = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description,
        }
        with open(cls.CSV_FILE, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)
        print("Entry added successfully")

    @classmethod
    def add_sample_data(cls, df):
        """Adds sample income and expense data for better plotting if the file is empty."""
        if df.empty:
            sample_data = [
                ("01-01-2025", 2000, "Income", "Salary"),
                ("02-01-2025", -150, "Expense", "Groceries"),
                ("03-01-2025", 500, "Income", "Freelance work"),
                ("04-01-2025", -200, "Expense", "Transport"),
                ("05-01-2025", -100, "Expense", "Entertainment"),
                ("06-01-2025", 1000, "Income", "Investment Returns"),
                ("07-01-2025", -50, "Expense", "Snacks"),
                ("08-01-2025", -300, "Expense", "Rent"),
                ("09-01-2025", 1500, "Income", "Freelance work"),
                ("10-01-2025", -250, "Expense", "Utilities"),
                ("11-01-2025", 100, "Income", "Side project"),
                ("12-01-2025", -200, "Expense", "Groceries"),
                ("13-01-2025", -150, "Expense", "Transport"),
                ("14-01-2025", 2500, "Income", "Salary"),
                ("15-01-2025", -300, "Expense", "Insurance"),
            ]
            with open(cls.CSV_FILE, "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(sample_data)
            print("Sample data added successfully.")

    @classmethod
    def get_transactions(cls, start_date, end_date):
        """Fetches transactions within the given date range."""
        df = pd.read_csv(cls.CSV_FILE)
        
        # Safely parse dates, invalid dates will be converted to NaT (Not a Time)
        df["date"] = pd.to_datetime(df["date"], format=cls.FORMAT, errors='coerce')
        
        # Filter out any rows where the date could not be parsed (NaT)
        df = df.dropna(subset=["date"])

        start_date = datetime.strptime(start_date, cls.FORMAT)
        end_date = datetime.strptime(end_date, cls.FORMAT)

        mask = (df["date"] >= start_date) & (df["date"] <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            print("No transactions found in the given date range.")
        else:
            print(
                f"\nTransactions from {start_date.strftime(cls.FORMAT)} to {end_date.strftime(cls.FORMAT)}:"
            )
            print(
                filtered_df.to_string(
                    index=False, formatters={"date": lambda x: x.strftime(cls.FORMAT)}
                )
            )

        filtered_df["amount"] = filtered_df["amount"].astype(float)
        total_income = filtered_df[filtered_df["category"] == "Income"]["amount"].sum()
        total_expense = filtered_df[filtered_df["category"] == "Expense"]["amount"].sum()

        print("\nSummary:")
        print(f"Total Income: ${total_income:.2f}")
        print(f"Total Expense: ${total_expense:.2f}")
        print(f"Net Savings: ${total_income - total_expense:.2f}")
        return filtered_df


def plot_transactions(df):
    """Plots income and expenses over time."""
    df["date"] = pd.to_datetime(df["date"], format=CSV.FORMAT)
    df.set_index("date", inplace=True)

    # Group and resample data by day
    income_df = (
        df[df["category"] == "Income"]["amount"]
        .resample("D")
        .sum()
        .reindex(pd.date_range(df.index.min(), df.index.max()), fill_value=0)
    )
    expense_df = (
        df[df["category"] == "Expense"]["amount"]
        .resample("D")
        .sum()
        .reindex(pd.date_range(df.index.min(), df.index.max()), fill_value=0)
    )

    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(income_df.index, income_df, label="Income", color="green")
    plt.plot(expense_df.index, expense_df, label="Expense", color="red")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title("Income and Expenses Over Time")
    plt.legend()
    plt.grid(True)
    plt.show()


def add():
    """Collects transaction details from the user and adds them to the CSV."""
    CSV.initialize_csv()
    date = get_date(
        "Enter the date of the transaction (dd-mm-yyyy) or enter for today's date: ",
        allow_default=True,
    )
    amount = get_amount()
    category = get_category()
    description = get_description()
    CSV.add_entry(date, amount, category, description)


def main():
    """Main program loop for managing transactions."""
    while True:
        print("\n1. Add a new transaction")
        print("2. View transactions and summary within a date range")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ")
        if choice == "1":
            add()
        elif choice == "2":
            start_date = get_date("Enter the start date (dd-mm-yyyy): ")
            end_date = get_date("Enter the end date (dd-mm-yyyy): ")
            df = CSV.get_transactions(start_date, end_date)
            if not df.empty and input("Do you want to see a plot? (y/n): ").lower() == "y":
                plot_transactions(df)
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
