import datetime
from typing import Iterable, Iterator, NamedTuple, TypedDict

from django.db.models import Max, Min, Q
from django.utils import timezone

from ..models import AppointmentType, Location

APPOINTMENT_TIME_FILTER = (
    Q(date__gt=timezone.now())
    | (Q(start_time__gte=timezone.now().time()) & Q(date=timezone.now())),
)


class AppointmentTuple(NamedTuple):
    start_time: datetime.time
    end_time: datetime.time
    date: datetime.date
    appointment_type: int
    location__name: str


class AppointmentTypeDict(TypedDict):
    name: str
    appointment_category: str
    appointments: Iterable[AppointmentTuple]


def create_appointment_type_list(
    appointment_types: Iterable,
    extra_filters: Iterable[Q] = APPOINTMENT_TIME_FILTER,
) -> list[AppointmentTypeDict]:
    """
    Creates a list of appointment types with their corresponding appointments.
    Annotates the query with the minimum creation date of the appointment and the maximum creation date of the appointment.
    The appointments only feature the fields date, start_time, end_time and the annotated fields.

    Args:
        appointment_types: A collection of appointment types.
        extra_filters (Iterable[Q], optional): A collection of additional filters to apply on appointments. Defaults to APPOINTMENT_TIME_FILTER.

    Returns:
        list: A list of dictionaries containing the appointmenttype name, category and their corresponding appointments.
    """

    appointment_types_list = []
    for appointment_type in appointment_types:
        appointments = (
            appointment_type.appointments.values(
                "end_time", "start_time", "date", "location__name"
            )
            .annotate(Min("creation_date"), Max("creation_date"))
            .filter(*extra_filters)
            .distinct()
        )

        if appointments:
            appointment_types_list.append(
                {
                    "name": appointment_type.name,
                    "appointment_category": appointment_type.appointment_category.name,
                    "appointments": appointments,
                }
            )
    return appointment_types_list


def create_appointment_type_list_from_list(
    appointments: list[AppointmentTuple],
) -> list[AppointmentTypeDict]:
    """
    Creates a list of appointment types with their corresponding appointments from a list of appointments.
    The appointments only feature the fields start_time, end_time and date in that order.

    Args:
        appointments (list[ tuple[datetime.time, datetime.time, datetime.date, AppointmentType] ]): A list of appointments.

    Returns:
        list[AppointmentTypeDict]: A list of dictionaries containing the appointmenttype name, category and their corresponding appointments.
    """
    appointment_types_dict = {}
    for appointment_type in AppointmentType.objects.all():
        appointment_types_dict[appointment_type.pk] = appointment_type

    appointment_types_list = {}
    for appointment in appointments:
        appointment_type = appointment_types_dict[appointment[3]]
        if appointment_type.name not in appointment_types_list:
            appointment_types_list[appointment_type.name] = {
                "name": appointment_type.name,
                "appointment_category": appointment_type.appointment_category.name,
                "appointments": [],
            }
        appointment_types_list[appointment_type.name]["appointments"].append(
            appointment
        )

    return list(appointment_types_list.values())


def filter_appointments_by_type(
    appointments: Iterable[AppointmentTuple], appointment_types: Iterable[int]
) -> Iterator[AppointmentTuple]:
    """
    filter_appointments_by_type filters appointments by their appointment type.

    Args:
        appointments (Iterable[AppointmentTuple]): A collection of appointments.
        appointment_types (Iterable[int]): A collection of appointment type ids.

    Returns:
        filter[AppointmentTuple]: A filter object containing the filtered appointments.
    """
    return filter(lambda appointment: appointment[3] in appointment_types, appointments)
