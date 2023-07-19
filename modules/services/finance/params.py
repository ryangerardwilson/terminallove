import calendar
import datetime
import os
import pytz
from dotenv import load_dotenv

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv(os.path.join(parent_dir, '.env'))

TIMEZONE=os.getenv('TIMEZONE')
tz=pytz.timezone(TIMEZONE)

DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD = os.getenv('DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD')

now = datetime.datetime.now(tz)
weekday_num = now.weekday()
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day = days_of_week[weekday_num]
today = now.strftime('%Y-%m-%d %H:%M:%S')
days_in_current_month = calendar.monthrange(now.year, now.month)[1]
days_left_in_current_month = days_in_current_month - now.day
last_day_of_current_year = datetime.datetime(now.year, 12, 31, tzinfo=tz)
days_left_in_current_year = (last_day_of_current_year - now).days

list_expense_logging_params = {
    "name": "list_expense_logging_params",
    "description": "Lists the parameters required to log an expense",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Listing runs from rgw-bot@GoogleCloudMySQL"]
            },
        },
        "required": []
    }
}

log_expenses = {
    "name": "log_expenses",
    "description": "Log the user's expense",
    "parameters": {
        "type": "object",
        "properties": {
            "value": {
                "type": "integer",
                "description": "The money spent by the user"
            },
            "particulars": {
                "type": "string",
                "description": "The item on which money was spent"
            },
            "expense_date": {
                "type": "string",
                "description": f"The timestamp of the expense in YYYY-MM-DD HH:MM:SS format. Default is {today}. Otherwise, this needs to be calculated relative from {today}"
            },
            "currency": {
                "type": "string",
                "enum": ["INR"]
            },
            "debt_id": {
                "type": "integer",
                "description": F"The id of the debt source used to fund the transaction. Default is {DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD}"
            },
            "is_debt_repayment": {
                "type": "boolean",
                "description": "If the expense relates to directly paying off a debt, such as a loan or a credit card bill. Default is false."
            },
            "is_earmarked_for_debt_repayment": {
                "type": "boolean",
                "description": "If the expense does not relate to directly paying off a debt(or loan or credit card bill), but is earmarked for that purpose. Default is false."
            },
            "today": {
                "type": "string",
                "enum": [today]
            }
        },
        "required": ["value", "particulars", "debt_id", "repaid_debt_id", "is_debt_repayment", "is_earmarked_for_debt_repayment"]
    }
}

log_debt_repayment = {
    "name": "log_debt_repayment",
    "description": "Log the user's debt repayments",
    "parameters": {
        "type": "object",
        "properties": {
            "value": {
                "type": "integer",
                "description": "The money repaid by the user"
            },
            "expense_date": {
                "type": "string",
                "description": f"The timestamp of the repayment date in YYYY-MM-DD HH:MM:SS format. Default is {today}. Otherwise, this needs to be calculated relative from {today}"
            },
            "currency": {
                "type": "string",
                "enum": ["INR"]
            },
            "debt_id": {
                "type": "integer",
                "description": F"The id of the debt repaid. Default is {DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD}"
            },
            "is_earmarked": {
                "type": "boolean",
                "description": "If the money is earmarked to repay the debt, instead of directly repaying the debt."
            },
            "today": {
                "type": "string",
                "enum": [today]
            }
        },
        "required": ["value", "debt_id", "is_earmarked"]
    }
}


list_expenses = {
    "name": "list_expenses",
    "description": "Lists the user's expense",
    "parameters": {
        "type": "object",
        "properties": {
            "days_ago_end": {
                "type": "integer",
                "description": "The number of days ago when the range ends. Default is 0."
            },
            "days_ago_start": {
                "type": "integer",
                "description": "The number of days ago when the range starts. This is optional."
            },
            "today": {
                "type": "string",
                "enum": [today]
            },
            "include_debt_repayment": {
                "type": "boolean",
                "description": "If expenses relating to paying off debts, such as a loan or a credit card bill, are to be excluded. Default is true."
            },
        },
        "required": ["exclude_debt_repayment"]
    }
}

update_expense_by_id = {
    "name": "update_expense_by_id",
    "description": "Update an expense by its id",
    "parameters": {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "description": "Expense id"
            },
            "value": {
                "type": "integer",
                "description": "The money spent by the user"
            },
            "particulars": {
                "type": "string",
                "description": "The item on which money was spent"
            },
            "expense_date": {
                "type": "string",
                "description": f"The timestamp of the expense in YYYY-MM-DD HH:MM:SS format. Default is {today}. Otherwise, this needs to be calculated relative from {today}"
            },
            "currency": {
                "type": "string",
                "enum": ["INR"]
            },
            "debt_id": {
                "type": "integer",
                "description": "The id of the debt source used to fund the transaction. Default is 14"
            },
            "repaid_debt_id": {
                "type": "integer",
                "description": f"The id of the debt paid by the transaction. Default is {DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD}"
            },
            "is_debt_repayment": {
                "type": "boolean",
                "description": "If the expense relates to paying off a debt, such as a loan or a credit card bill. Default is false."
            },
            "is_earmarked_for_debt_repayment": {
                "type": "boolean",
                "description": "If the expense does not directly pay off a debt(or loan or credit card bill), but is earmarked for that purpose. Default is false."
            },
            "today": {
                "type": "string",
                "enum": [today]
            }
        },
        "required": ["id"]
    }
}

delete_expenses_by_ids = {
    "name": "delete_expenses_by_ids",
    "description": "Delete expenses by their ids",
    "parameters": {
        "type": "object",
        "properties": {
            "ids": {
                "type": "string",
                "description": "The ids to be deleted separated by camel case. For instance ids 4 and 5 would be 4_5"
            },
        },
        "required": ["ids"]
    }
}

display_expenses_line_chart = {
    "name": "display_expenses_line_chart",
    "description": "Plots an ascii line chart of the users expenses",
    "parameters": {
        "type": "object",
        "properties": {
            "days_ago_end": {
                "type": "integer",
                "description": "The number of days ago when the range ends. Default is 0."
            },
            "days_ago_start": {
                "type": "integer",
                "description": "The number of days ago when the range starts. This is optional."
            },
            "is_cumulative": {
                "type": "boolean",
                "description": "If the user has requested cumulative expenses. Default is false."
            },
            "today": {
                "type": "string",
                "enum": [today]
            },
            "include_debt_repayment": {
                "type": "boolean",
                "description": "If expenses relating to paying off debts, such as a loan or a credit card bill, are to be included. Default is true."
            },
        },
        "required": ["is_cumulative", "include_debt_repayment"]
    }
}



log_debts = {
    "name": "log_debts",
    "description": "Log the user's debt",
    "parameters": {
        "type": "object",
        "properties": {
            "source": {
                "type": "integer",
                "description": "The lender"
            },
            "total_amount": {
                "type": "integer",
                "description": "The total amount borrowed"
            },
            "outstanding": {
                "type": "integer",
                "description": "The outstanding amount due"
            },
            "interest_rate": {
                "type": "integer",
                "description": "The interest rate"
            },
            "currency": {
                "type": "string",
                "enum": ["INR"]
            },
            "today": {
                "type": "string",
                "enum": [today]
            }
        },
        "required": ["source", "total_amount"]
    }
}

insert_debt_status_log = {
    "name": "insert_debt_status_log",
    "description": "Insert a debt status log against a debt id",
    "parameters": {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "description": "Debt id"
            },
            "total_amount": {
                "type": "integer",
                "description": "The total amount borrowed"
            },
            "outstanding": {
                "type": "integer",
                "description": "The outstanding amount due"
            },
            "today": {
                "type": "string",
                "enum": [today]
            }
        },
        "required": ["id"]
    }
}

recalculate_debts = {
    "name": "recalculate_debts",
    "description": "Recalculates the outstanding amount of the user's debts",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Listing debts from rgw-bot@GoogleCloudMySQL"]
            },
        },
        "required": []
    }
}


list_debts = {
    "name": "list_debts",
    "description": "Lists the user's debts",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Listing debts from rgw-bot@GoogleCloudMySQL"]
            },
        },
        "required": []
    }
}

list_debt_status_logs = {
    "name": "list_debt_status_logs",
    "description": "Lists status logs against a given debt id showing how much the total amount and outstanding have changed over time",
    "parameters": {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "description": "Debt id"
            },
        },
        "required": []
    }
}

update_debt_by_id = {
    "name": "update_debt_by_id",
    "description": "Update a debt by its id",
    "parameters": {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "description": "Debt id"
            },
            "source": {
                "type": "integer",
                "description": "The lender"
            },
            "total_amount": {
                "type": "integer",
                "description": "The total amount borrowed"
            },
            "outstanding": {
                "type": "integer",
                "description": "The outstanding amount due"
            },
            "interest_rate": {
                "type": "integer",
                "description": "The interest rate"
            },
            "currency": {
                "type": "string",
                "enum": ["INR"]
            },
            "today": {
                "type": "string",
                "enum": [today]
            }
        },
        "required": ["id"]
    }
}

update_debt_status_log_by_id = {
    "name": "update_debt_status_log_by_id",
    "description": "Update a debt status log by its id",
    "parameters": {
        "type": "object",
        "properties": {
            "log_id": {
                "type": "integer",
                "description": "Debt status log id"
            },
            "total_amount": {
                "type": "integer",
                "description": "The total amount borrowed"
            },
            "outstanding": {
                "type": "integer",
                "description": "The outstanding amount due"
            },
            "today": {
                "type": "string",
                "enum": [today]
            }
        },
        "required": ["log_id"]
    }
}

delete_debts_by_ids = {
    "name": "delete_debts_by_ids",
    "description": "Delete debts by their ids",
    "parameters": {
        "type": "object",
        "properties": {
            "ids": {
                "type": "string",
                "description": "The ids to be deleted separated by camel case. For instance ids 4 and 5 would be 4_5"
            },
        },
        "required": ["ids"]
    }
}

delete_debt_status_logs_by_ids = {
    "name": "delete_debt_status_logs_by_ids",
    "description": "Delete debt status logs by their ids. Unike delete_debts_by_ids, this function deletes status logs of debts.",
    "parameters": {
        "type": "object",
        "properties": {
            "ids": {
                "type": "string",
                "description": "The ids to be deleted separated by camel case. For instance ids 4 and 5 would be 4_5"
            },
        },
        "required": ["ids"]
    }
}

display_debt_status_logs_line_chart = {
    "name": "display_debt_status_logs_line_chart",
    "description": "Plots an ascii line chart of the status of the debt with a specific id over the given range of days",
    "parameters": {
        "type": "object",
        "properties": {
            "debt_id": {
                "type": "integer",
                "description": "The id of the debt whose logs are be charted"
            },
            "days_ago_end": {
                "type": "integer",
                "description": "The number of days ago when the range ends. Default is 0."
            },
            "days_ago_start": {
                "type": "integer",
                "description": "The number of days ago when the range starts. Default is 120."
            },
            "today": {
                "type": "string",
                "enum": [today]
            }
        },
        "required": ["debt_id"]
    }
}



