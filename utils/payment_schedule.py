import calendar
import pandas as pd
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

CURRENT_DATE = date(2024, 12, 3)


# generate payment schedule ----------------------------------------------------------------
def normalize_scheduled_day(frequency: str, scheduled_day: str):
    """
    For monthly allowances, convert day strings into an integer.
    For weekly/biweekly, return a lowercase weekday.
    For daily, simply return "daily".
    """
    freq = frequency.lower()
    sd = scheduled_day.lower()

    if freq == "monthly":
        if sd in ["1st", "first_day"]:
            return 1

        elif sd in ["15th", "fifteenth_day"]:
            return 15

        else:
            # Attempt to extract numeric digits (e.g., "20th" -> 20)
            try:
                return int(''.join(filter(str.isdigit, sd)))
            except Exception as e:
                raise ValueError(f"Unrecognized monthly scheduled_day: {scheduled_day}") from e

    elif freq in ["weekly", "biweekly"]:
        return sd  # assume day names are provided, e.g., "monday", "sunday", etc.

    elif freq == "daily":
        return sd  # not used in calculation; placeholder

    else:
        raise ValueError(f"Unsupported frequency: {frequency}")

def get_next_payment_date(frequency: str, scheduled_day, base_date: date, current_date=CURRENT_DATE) -> date:
    """
    Compute the next payment date based on the allowance frequency and scheduled day.
    
    For daily allowances, returns the next day.
    For weekly, uses the weekday name.
    For biweekly, schedules payments only on the first and third occurrence
      of the target weekday in the month.
    For monthly, uses the integer day (with month rollover if needed).
    """
    freq = frequency.lower()
    
    if freq == "daily":
        return current_date + timedelta(days=1)
    
    elif freq == "weekly":
        # Use the standard weekly logic.
        day_mapping = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6
        }
        target_weekday = day_mapping.get(scheduled_day.lower())
        if target_weekday is None:
            raise ValueError(f"Invalid scheduled_day for weekly: {scheduled_day}")
        days_ahead = (target_weekday - base_date.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        return base_date + timedelta(days=days_ahead)
    
    elif freq == "biweekly":
        # Biweekly: Payment only on the first and third occurrence of scheduled_day in the month.
        day_mapping = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6
        }
        target_weekday = day_mapping.get(scheduled_day.lower())
        if target_weekday is None:
            raise ValueError(f"Invalid scheduled_day for biweekly: {scheduled_day}")
        
        # Define a helper to find the valid (1st and 3rd) occurrences in a given year/month.
        def valid_biweekly_dates(year: int, month: int):
            _, num_days = calendar.monthrange(year, month)
            weekday_dates = [date(year, month, d) for d in range(1, num_days + 1)
                             if date(year, month, d).weekday() == target_weekday]
            valid = []
            if len(weekday_dates) >= 1:
                valid.append(weekday_dates[0])  # first occurrence

            if len(weekday_dates) >= 3:
                valid.append(weekday_dates[2])  # third occurrence

            return valid
        
        # Check current month.
        year, month = current_date.year, current_date.month
        valid_dates = valid_biweekly_dates(year, month)
        for dt in valid_dates:
            if dt > current_date:
                return dt
        
        # If none found in the current month, move to the next month.
        next_month_date = current_date + relativedelta(months=1)
        year, month = next_month_date.year, next_month_date.month
        valid_dates = valid_biweekly_dates(year, month)
        if valid_dates:
            return valid_dates[0]
        
        else:
            raise ValueError("No valid biweekly payment date found in the next month.")
    
    elif freq == "monthly":
        # For monthly frequency, scheduled_day is expected to be an integer.
        day_num = scheduled_day  # already normalized as an integer.
        last_day = calendar.monthrange(base_date.year, base_date.month)[1]
        if base_date.day < day_num <= last_day:
            return date(base_date.year, base_date.month, day_num)
        
        else:
            next_month = base_date + relativedelta(months=1)
            last_day_next = calendar.monthrange(next_month.year, next_month.month)[1]
            day_to_use = min(day_num, last_day_next)
            return date(next_month.year, next_month.month, day_to_use)
    
    else:
        raise ValueError(f"Unsupported frequency: {frequency}")

def update_allowance_backend_table(original_df: pd.DataFrame, events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Update the original allowance_backend_table using the events log.
    The following fields are updated using the latest event for each user:
        - frequency
        - day
        - updated_at
        - next_payment_day (computed from the expected next payment date)
    The original uuid, creation_date, and status fields remain unchanged.
    """
    # Ensure event.timestamp is in datetime format.
    events_df['event.timestamp'] = pd.to_datetime(events_df['event.timestamp'])
    
    # Compute the latest settings per user from events.
    computed = {}
    grouped = events_df.groupby('user.id')
    for user_id, group in grouped:
        # Latest event for this user
        latest_event = group.sort_values('event.timestamp').iloc[-1]
        frequency = latest_event['allowance.scheduled.frequency']
        raw_day = latest_event['allowance.scheduled.day']
        normalized_day = normalize_scheduled_day(frequency, raw_day)

        try:
            expected_date = get_next_payment_date(frequency, normalized_day, CURRENT_DATE)

        except Exception as e:
            expected_date = None

        updated_at = group['event.timestamp'].max()
        computed[user_id] = {
            'frequency': frequency,
            'day': raw_day,
            'next_payment_day': float(expected_date.day) if expected_date is not None else None,
            'updated_at': updated_at
        }
    
    # Update original rows where computed events exist.
    updated_rows = []
    for idx, row in original_df.iterrows():
        user_id = row['uuid']
        if user_id in computed:
            row['frequency'] = computed[user_id]['frequency']
            row['day'] = computed[user_id]['day']
            row['next_payment_day'] = computed[user_id]['next_payment_day']
            row['updated_at'] = computed[user_id]['updated_at']
        updated_rows.append(row)

    return pd.DataFrame(updated_rows)

def generate_payment_schedule_backend_table(allowance_backend_df: pd.DataFrame, only_enabled=True) -> pd.DataFrame:
    """
    For enabled allowances, generate the payment schedule record.
    Each user should have one active record with payment_date aligning with the allowance.
    """

    if only_enabled:
        allowance_backend_df = allowance_backend_df[allowance_backend_df['status'] == "enabled"]
        
    records = []
    for _, row in allowance_backend_df.iterrows():
        record = {
            "uuid": row['uuid'],
            "payment_date": row['next_payment_day']  # this is the day-of-month (float)
        }
        records.append(record)
    return pd.DataFrame(records)

def get_events_logs(allowance_events, uuid) -> pd.DataFrame:

    user_events = allowance_events[allowance_events['user.id'] == uuid]
    user_events = user_events.sort_values('event.timestamp')
    
    return user_events
