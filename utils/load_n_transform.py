import json
import pandas as pd


# load and transform data ----------------------------------------------------------------
def parse_unix_or_date(val):
    """
    Convert a mixed-format value from the updated_at column to a datetime.
    If the value is numeric (or a numeric string), treat it as a Unix timestamp.
    Otherwise, assume it's an ISO-formatted datetime string.
    """
    # Check if the value is a string and represents digits only.
    if isinstance(val, str) and val.isdigit():
        return pd.to_datetime(val, unit='s')
    
    # If the value is already numeric, convert from Unix timestamp.
    elif isinstance(val, (int, float)):
        return pd.to_datetime(val, unit='s')
    
    else:
        # Otherwise, attempt to parse as a datetime string.
        return pd.to_datetime(val, errors='coerce', format='ISO8601')

def get_allowance_backend_table(path='data/allowance_backend_table.csv'):

    allowance_backend_table = pd.read_csv(path)

    # date adj
    allowance_backend_table['creation_date'] = allowance_backend_table['creation_date'].apply(parse_unix_or_date)
    allowance_backend_table['updated_at'] = allowance_backend_table['updated_at'].apply(parse_unix_or_date)

    allowance_backend_table = allowance_backend_table.sort_values(['creation_date'])

    return allowance_backend_table

def get_payment_schedule_backend_table(path='data/payment_schedule_backend_table.csv'):

    payment_schedule_backend_table = pd.read_csv(path)

    # rename uuid column
    payment_schedule_backend_table.rename(columns={'user_id': 'uuid'}, inplace=True)

    return payment_schedule_backend_table

def get_allowance_events(path='data/allowance_events.json'):

    with open(path) as f:
        allowance_events_json = json.load(f)

    allowance_events = pd.json_normalize(allowance_events_json)

    # date adj
    allowance_events['event.timestamp'] = allowance_events['event.timestamp'].apply(parse_unix_or_date)

    return allowance_events
