import asyncio
import datetime
from typing import Coroutine

import httpx
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup, Doctype, SoupStrainer
from django.core.mail import mail_admins

from .models import (
    Appointment,
    AppointmentCategory,
    AppointmentType,
    Location,
    ScraperRun,
)
from .utils.time import make_aware_no_error

URL = (
    "https://tevis.ekom21.de/stdar/"  # Link zum Terminvergabe Tool der Stadt Darmstadt
)
time_forms = SoupStrainer("form", attrs={"class": "suggestion_form"})


async def add_appointment(
    start_time: datetime.time,
    end_time: datetime.time,
    date: datetime.date,
    appointment_type: AppointmentType,
    location: Location,
    scraper_run: ScraperRun,
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
        start_time=start_time,
        end_time=end_time,
        date=date,
        location=location,
        appointment_type=appointment_type,
    ).aget_or_create(
        start_time=make_aware_no_error(start_time),
        end_time=make_aware_no_error(end_time),
        date=date,
        location=location,
        appointment_type=appointment_type,
    )
    await appointment.scraper_run.aadd(scraper_run)


async def fetch_appointment(
    client: httpx.AsyncClient,
    appointment_category: int,
    appointment_type: AppointmentType,
    scraper_run: ScraperRun,
) -> list[Coroutine]:
    async for location in appointment_type.location.all():
        request = await client.post(
            "location",
            params={
                "mdt": appointment_category,
                f"cnc-{appointment_type.index}": 1,
            },
            data={
                "loc": location.index,
                "select_location": location.descriptor,
            },
            follow_redirects=True,
        )
        try:
            request.raise_for_status()
        except httpx.HTTPStatusError as e:
            mail_admins(
                "Fehler beim Aufruf der Terminvergabe von Darmstadt",
                f"Der Scraper hat, beim Versuch die Termine zu ermitteln, einen Verbindungsfehler erhalten:\n{e}",
            )
            raise e

        soup = BeautifulSoup(request.text, "lxml", parse_only=time_forms)
        tasks = []

        for element in soup:
            if isinstance(element, Doctype):
                element.extract()
                continue
            try:
                start_time = int(
                    element.findNext("input", attrs={"name": "start"})["value"]
                )  # in minutes
                end_time = int(
                    element.findNext("input", attrs={"name": "end"})["value"]
                )  # in minutes
                date: str = element.findNext("input", attrs={"name": "date"})[
                    "value"
                ]  # format YYYYMMDD
            except TypeError:
                mail_admins(
                    "Fehler beim Parsen der Termine",
                    f"Das nachfolgende Terminelement konnte nicht geparst werden.\nURL:{request.url}\nParsed element:\n{element}\nSoup:\n{soup}\nAnfragetext:\n{request.text}",
                )
                continue
            tasks.append(
                add_appointment(
                    start_time=datetime.time(
                        minute=start_time % 60, hour=start_time // 60
                    ),
                    end_time=datetime.time(minute=end_time % 60, hour=end_time // 60),
                    date=datetime.datetime.strptime(date, "%Y%m%d").date(),
                    appointment_type=appointment_type,
                    location=location,
                    scraper_run=scraper_run,
                )
            )
    return tasks


async def fetch_appointments(
    department_index: int,
    appointment_category: int,
    appointment_types,
    scraper_run: ScraperRun,
):
    """
    fetch_appointments looks for all available appointments of a specific type

    Args:
        appointment_category (int): the appointment category index used in the url
        appointment_type (int): the appointment type index used in the url
    """
    if await appointment_types.acount() == 0:
        return
    async with httpx.AsyncClient(
        base_url=URL, headers={"user-agent": "Termin-Scraper/1.0"}, max_redirects=50
    ) as client:
        await client.get("select2", params={"md": department_index})
        await client.get(
            "location",
            params={
                "mdt": appointment_category,
                f"cnc-{(await appointment_types.afirst()).index}": 1,
            },
        )
        tasks = []
        async for appointment_type in appointment_types.aiterator():
            tasks.extend(
                await fetch_appointment(
                    client, appointment_category, appointment_type, scraper_run
                )
            )

        await asyncio.gather(*tasks)


async def fetch_all_types():
    """
    fetch_all_types fetches appointments for all types
    """
    appointment_categories = await sync_to_async(
        AppointmentCategory.objects.prefetch_related("types", "department").all
    )()
    scraper_run = ScraperRun()
    await scraper_run.asave()
    await asyncio.gather(
        *[
            fetch_appointments(
                appointment_category.department.index,
                appointment_category.index,
                appointment_category.types.filter(active=True),
                scraper_run,
            )
            async for appointment_category in appointment_categories
        ]
    )
    await scraper_run.asave()
