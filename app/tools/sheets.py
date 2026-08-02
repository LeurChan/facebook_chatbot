"""Save a customer's installation booking into Google Sheets."""
from datetime import datetime, timedelta

import gspread
from langchain_core.tools import tool
from app.config import settings

# Connect ONCE at import; reuse the worksheet on every call.
_worksheet = (
    gspread.service_account(filename=settings.google_sheets_credentials_path)
    .open_by_key(settings.google_sheets_id)
    .sheet1
)


@tool
def book_installation(name: str, phone: str, item_or_service: str,
                      preferred_time: str, motorbike_model: str = "") -> str:
    """Save a customer's motorbike accessory installation or order to the shop's records.
    Call this ONLY after you have the customer's name, phone, the requested item/service,
    and their preferred date/time.

    Args:
        name: customer's full name
        phone: customer's phone number
        item_or_service: the accessory or installation service requested (e.g., LED lights, phone mount)
        preferred_time: preferred date and/or time for the visit
        motorbike_model: the make and model of the customer's motorbike (optional)
    """
    now = datetime.now()
    
    # Check existing records to prevent rapid duplicate writes from agent loops
    try:
        records = _worksheet.get_all_records()
        for row in records:
            row_time_str = str(row.get("Timestamp", ""))
            if row_time_str:
                row_time = datetime.strptime(row_time_str, "%Y-%m-%d %H:%M:%S")
                if (
                    str(row.get("Phone")) == phone
                    and str(row.get("Item/Service")) == item_or_service
                    and (now - row_time) < timedelta(seconds=60)
                ):
                    return f"Appointment already logged for {name}."
        print("Duplicate check passed.")
    except Exception as e:
        print(f"Skipping duplicate check due to error: {e}")

    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # Appends columns to your Google Sheet
    _worksheet.append_row([timestamp, name, phone, item_or_service, preferred_time, motorbike_model])
    
    return f"Installation appointment saved for {name} ({item_or_service}, {preferred_time})."