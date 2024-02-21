from collections import defaultdict
from datetime import datetime, timedelta

import pytz

from .dbbase.ScoreCounter import RecordDAO


class DailyNumberLimiter:
    tz = pytz.timezone('Asia/Shanghai')

    def __init__(self, max_num):
        self.today = -1
        self.count = defaultdict(int)
        self.max = max_num

    def check(self, key) -> bool:
        now = datetime.now(self.tz)
        day = (now - timedelta(hours=5)).day
        if day != self.today:
            self.today = day
            self.count.clear()
        return bool(self.count[key] < self.max)
    
    def check_week(self, key) -> bool:
        current_date = datetime.now(self.tz)
        this_year, this_week, _ = current_date.isocalendar()
        day = int(str(this_year) + str(this_week))
        if day != self.today:
            self.today = day
            self.count.clear()
        return bool(self.count[key] < self.max)
    
    def get_num(self, key):
        return self.count[key]

    def increase(self, key, num=1):
        self.count[key] += num

    def reset(self, key):
        self.count[key] = 0


recorddb = RecordDAO()


class DailyAmountLimiter(DailyNumberLimiter):
    def __init__(self, types, max_num, reset_hour):
        super().__init__(max_num)
        self.reset_hour = reset_hour
        self.type = types

    def check(self, key) -> bool:
        now = datetime.now(self.tz)
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        day = (now - timedelta(hours=self.reset_hour)).day
        if day != recorddb.get_date(key):
            recorddb.set_date(day, key)
            recorddb.clear_key(key)
        return bool(recorddb.get_num(key) < self.max)
    
    def check_week(self, key) -> bool:
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        current_date = datetime.now(self.tz)
        this_year, this_week, _ = current_date.isocalendar()
        day = int(str(this_year) + str(this_week))
        if day != recorddb.get_date(key):
            recorddb.set_date(day, key)
            recorddb.clear_key(key)
        return bool(recorddb.get_num(key) < self.max)
    
    def check10(self, key) -> bool:
        now = datetime.now(self.tz)
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        day = (now - timedelta(hours=self.reset_hour)).day
        if day != recorddb.get_date(key):
            recorddb.set_date(day, key)
            recorddb.clear_key(key)
        return bool(recorddb.get_num(key) < 10)

    def get_num(self, key):
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        return recorddb.get_num(key)

    def increase(self, key, num=1):
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        recorddb.increment_key(key, num)

    def reset(self, key):
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        recorddb.clear_key(key)
