# Darmstadt Terminetracker

Eine Django Webapp zum tracken der verfügbaren Termine des Bürgerbüros und anderen Behörden in Darmstadt.

## Setup

1. `pip install git+https://github.com/Atlasfreak/darmstadt_termine.git`
2. In `settings.py` `darmstadt_termine` zu den `INSTALLED_APPS` hinzufügen.
3. `darmstadt_termine.urls` an geeigneter Stelle in urls.py einfügen.
4. Den Befehl `migrate` ausführen, um die Datenbank korrekt aufzusetzen.
5. Mit dem Kommandozeilenbefehl `scraper_run` den Webscraper ausführen und die aktuell verfügbaren Termine in die Datenbank schreiben.
6. Mit dem Kommandozeilenbefehl `send_notifications` E-Mail Benachrichtigungen verschicken.

Genaue Erklärungen der Befehle können mit `help <befehl>` erhalten werden.

## Development

1. Eine neue Django App erstellen
2. In den Ordner der Django App dieses Repository klonen
3. `poetry install`
4. Schritte 2-4 aus [Setup](#setup) durchführen
5. Der Debug Server kann dann aus dem geklonten Repository mit `python ../manage.py runserver` gestartet werden
