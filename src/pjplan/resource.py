from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional

from pjplan import IWorkCalendar, DEFAULT_CALENDAR, Task


class IResource(ABC):
    """A resource is a person, machine, or any other entity that is necessary to perform work (Task)"""

    def __init__(self, name: str):
        """
        :param name: Unique Resource Name
        """
        self.name = name

    @abstractmethod
    def get_available_units(self, date: datetime, task: Optional[Task] = None) -> float:
        """
        Returns the number of available working hours of a resource on a specified date
        :param date: date
        :param task: a task that requires resources. None, if there is no specific task
        :return: number of available resource hours
        """
        pass

    def get_nearest_availability_date(self, start_date: datetime, direction: int, max_days=100000) -> datetime:
        """
        Returns the nearest date of resource availability, starting from 'start_date'
        :param direction: 1 or -1
        :param start_date: search start date
        :param max_days: maximum search interval (in days)
        :return: availability date
        """
        step = 0
        while step < max_days:
            if direction < 0:
                if self.get_available_units(start_date - timedelta(days=1), None) > 0.0:
                    return start_date
            else:
                if self.get_available_units(start_date, None) > 0.0:
                    return start_date
            start_date += timedelta(days=direction)
            step += 1

        raise RuntimeError(
            "Can't find nearest availability time for resource", self.name,
            "after", start_date.strftime('%Y-%m-%d')
        )

    def reserve(self, date: datetime, task: Task, units: float):
        pass


class Resource(IResource):

    def __init__(
            self,
            name: str,
            calendar: IWorkCalendar = DEFAULT_CALENDAR
    ):
        """
        :param name: unique resource name
        :param calendar: work calendar

        Example of availability intervals:
        availability = [(datetime(2000, 1, 1), 50), (datetime(2000, 2, 1), 100)]
        means that:
        1. Until 2000-01-01, the resource is unavailable
        2. From 2000-01-01 to 2000-02-01, the resource is 50% available
        3. After 2000-02-01, the resource is 100% available
        """
        super().__init__(name)
        self.calendar = calendar

    def get_available_units(self, date: datetime, task: Optional[Task] = None) -> float:
        units = self.calendar.get_available_units(date)
        return 0 if units is None else units

    def __str__(self):
        return self.name

    def __repr__(self):
        res = f'{self.name}\n'
        res += self.calendar.__repr__()
        return res


DEFAULT_RESOURCE = Resource("default")
