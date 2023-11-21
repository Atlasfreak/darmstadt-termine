import asyncio
import datetime
from typing import Coroutine

import httpx
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup, SoupStrainer
from django.core.mail import mail_admins
from django.db.models import Q
from django.utils import timezone

from .models import Appointment, AppointmentCategory, AppointmentType
from .utils.time import make_aware_no_error

URL = (
    "https://tevis.ekom21.de/stdar/"  # Link zum Terminvergabe Tool der Stadt Darmstadt
)


async def add_appointment(
    start_time: datetime.time,
    end_time: datetime.time,
    date: datetime.date,
    appointment_type: AppointmentType,
):
    """
    add_appointment writes the appointment to the database
    if no appointment with the same data was create in the last 40 seconds
    else it retrives it and always adds the type

    Args:
        start_time (datetime.time): the start time of the appointment
        end_time (datetime.time): the end time of the appointment
        date (datetime.date): the date of the appointment
        appointment_type (AppointmentType): the type of the appointment
    """
    appointment, _ = await Appointment.objects.filter(
        Q(creation_date__gt=timezone.now() - datetime.timedelta(seconds=40))
    ).aget_or_create(
        start_time=make_aware_no_error(start_time),
        end_time=make_aware_no_error(end_time),
        date=date,
    )
    await appointment.appointment_type.aadd(appointment_type)


async def fetch_appointment(
    client: httpx.AsyncClient,
    appointment_category: int,
    appointment_type: AppointmentType,
) -> list[Coroutine]:
    request = await client.post(
        "suggest",
        params={
            "mdt": appointment_category,
            f"cnc-{appointment_type.index}": 1,
        },
        data={
            "loc": 43,
            "select_location": "KFZ-Zulassungsbehörde+(Gebäude+B)+auswählen",
        },
    )
    try:
        request.raise_for_status()
    except httpx.HTTPStatusError as e:
        mail_admins(
            "Fehler beim Aufruf der Terminvergabe von Darmstadt",
            f"Der Scraper hat, beim Versuch die Termine zu ermitteln, einen Verbindungsfehler erhalten:\n{e}",
        )
        raise e
    time_forms = SoupStrainer("form", attrs={"class": "suggestion_form"})
    soup = BeautifulSoup(request.text, "html.parser", parse_only=time_forms)
    tasks = []
    for element in soup:
        start_time = int(
            element.findNext("input", attrs={"name": "start"})["value"]
        )  # in minutes
        end_time = int(
            element.findNext("input", attrs={"name": "end"})["value"]
        )  # in minutes
        date: str = element.findNext("input", attrs={"name": "date"})[
            "value"
        ]  # format YYYYMMDD
        tasks.append(
            add_appointment(
                start_time=datetime.time(minute=start_time % 60, hour=start_time // 60),
                end_time=datetime.time(minute=end_time % 60, hour=end_time // 60),
                date=datetime.datetime.strptime(date, "%Y%m%d").date(),
                appointment_type=appointment_type,
            )
        )
    return tasks


async def fetch_appointments(appointment_category: int, appointment_types):
    """
    fetch_appointments looks for all available appointments of a specific type

    Args:
        appointment_category (int): the appointment category index used in the url
        appointment_type (int): the appointment type index used in the url
    """
    async with httpx.AsyncClient(
        base_url=URL, headers={"user-agent": "Termin-Scraper/1.0"}, max_redirects=50
    ) as client:
        await client.get("select2", params={"md": 5})
        await client.get(
            "suggest",
            params={
                "mdt": appointment_category,
                f"cnc-{(await appointment_types.afirst()).index}": 1,
            },
        )
        tasks = []
        async for appointment_type in appointment_types.aiterator():
            tasks.extend(
                await fetch_appointment(client, appointment_category, appointment_type)
            )
        await asyncio.gather(*tasks)


async def fetch_all_types():
    """
    fetch_all_types fetches appointments for all types
    """
    appointment_categories = await sync_to_async(
        AppointmentCategory.objects.prefetch_related("types").all
    )()
    await asyncio.gather(
        *[
            fetch_appointments(appointment_category.index, appointment_category.types)
            async for appointment_category in appointment_categories
        ]
    )
