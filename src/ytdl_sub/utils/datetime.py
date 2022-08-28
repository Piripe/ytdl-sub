from typing import Optional

from yt_dlp import DateRange

from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.validators.string_datetime import StringDatetimeValidator


def to_date_range_hack(
    before: Optional[StringDatetimeValidator], after: Optional[StringDatetimeValidator]
) -> Optional[DateRange]:
    """
    Workaround for channel before/after support.

    Returns
    -------
    Date range if the 'before' or 'after' is defined. None otherwise.
    """
    start: Optional[str] = None
    end: Optional[str] = None

    if after:
        start = after.apply_formatter(variable_dict={})

    if before:
        end = before.apply_formatter(variable_dict={})

    if start or end:
        return DateRange(start=start, end=end)

    return None


def to_date_range(
    before: Optional[StringDatetimeValidator],
    after: Optional[StringDatetimeValidator],
    overrides: Overrides,
) -> Optional[DateRange]:
    """
    Returns
    -------
    Date range if the 'before' or 'after' is defined. None otherwise.
    """
    start: Optional[str] = None
    end: Optional[str] = None

    if after:
        start = overrides.apply_formatter(formatter=after)

    if before:
        end = overrides.apply_formatter(formatter=before)

    if start or end:
        return DateRange(start=start, end=end)

    return None
