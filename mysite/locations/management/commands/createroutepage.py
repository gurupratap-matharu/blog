import random
from argparse import ArgumentParser

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from wagtail.rich_text import RichText

from locations.models import RouteIndexPage, RoutePage
from partners.models import PartnerPage
from trips.models import Route


class Command(BaseCommand):
    help = "Programmatically create a draft version of a Route page from a route data model."

    route = None

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("route_ids", nargs="*", type=int)

    def handle(self, *args, **options) -> str:
        created = 0
        route_ids = options["route_ids"]
        qs = Route.objects.filter(id__in=route_ids)

        for obj in qs:
            try:
                RoutePage.objects.get(code=obj.code)
            except RoutePage.DoesNotExist:
                self.create_page(obj)
                created += 1

        return f"Done. Created {created} pages"

    def create_page(self, obj: Route) -> bool:
        """
        Creates a single RoutePage from the route object nested underthe RouteIndex page tree.
        """

        self.success(f"creating page for {obj}...")
        self.route = obj

        title = self.get_title()
        slug = self.get_slug()
        seo_title = self.get_seo_title()
        search_description = self.get_search_description()
        social_text = self.get_social_text()
        listing_title = self.get_listing_title()
        listing_summary = search_description
        intro = self.get_intro()

        route_index_page = RouteIndexPage.objects.first()
        route_page = RoutePage(
            title=title,
            slug=slug,
            seo_title=seo_title,
            search_description=search_description,
            social_text=social_text,
            listing_title=listing_title,
            listing_summary=listing_summary,
            intro=intro,
            code=self.route.code,
        )

        # this is how stream fields need to be added
        route_page.companies.append(self.get_companies())
        route_page.faq.append(self.get_faq())

        route_index_page.add_child(instance=route_page)
        route_page.save()

        print(f"title: {title}")
        print(f"slug: {slug}")
        print(f"seo_title: {seo_title}")
        print(f"search_description: {search_description}")
        print(f"social_text: {social_text}")
        print(f"listing_title: {listing_title}")
        print(f"listing_summary:{listing_summary}")
        print(f"code:{self.route.code}")
        print(f"intro:{intro}")
        print(f"companies:{self.get_companies()}")
        label, data = self.get_faq()
        print(label)
        for x in data["item"]:
            print(x["question"])
            print(x["answer"])
        print("\n")

        return True

    # methods to generate page specific fields
    def get_title(self) -> str:
        return f"{self.route.origin} a {self.route.destination}: horarios y precios"

    def get_slug(self) -> str:
        text = f"{self.route.origin} a {self.route.destination}"
        return slugify(text)

    def get_seo_title(self) -> str:
        return f"{self.route.origin} → {self.route.destination}: Horarios, Precios y Empresas | Ventanita"

    def get_search_description(self) -> str:
        origin, dest = self.route.origin, self.route.destination

        templates = [
            (
                f"Conocé cómo viajar en bus de {origin} a {dest} en Argentina. "
                f"Informate sobre la ruta, los horarios y los detalles de tu viaje con Ventanita."
            ),
            (
                f"¿Viajás de {origin} a {dest}? Descubrí información sobre el recorrido en micro, "
                f"consultá detalles de la ruta y planificá tu próximo viaje con Ventanita."
            ),
            (
                f"Encontrá toda la información para tu viaje en micro desde {origin} a {dest}. "
                f"Horarios, terminales y tips para planificar tu próxima escapada con Ventanita."
            ),
            (
                f"Consultá los horarios, precios estimados y empresas de micro para viajar de {origin} a {dest}. "
                f"¡Planificá tu viaje gratis antes de ir a la terminal con Ventanita!"
            ),
            (
                f"Compará las salidas de micros de {origin} a {dest}. Encontrá precios mínimos, empresas operadoras, "
                f"frecuencias y el viaje más rápido en Ventanita."
            ),
        ]
        return random.choice(templates)

    def get_social_text(self) -> str:
        return self.get_seo_title()

    def get_listing_title(self) -> str:
        return self.get_seo_title()

    def get_listing_summary(self) -> str:
        return self.get_search_description()

    def get_intro(self) -> str:
        origin, dest = self.route.origin, self.route.destination
        num_departures = self.route.num_departures
        num_companies = self.route.num_companies
        min_duration = self.route.get_min_duration_display()

        desc = f"Hay {num_departures} salidas con {num_companies} empresas de micro desde {origin} a {dest} con una duración mínima de {min_duration}."
        return desc

    def get_faq(self) -> tuple[str, dict]:
        origin, dest = self.route.origin, self.route.destination
        low_d = self.route.get_min_duration_display()
        avg_d = self.route.get_avg_duration_display()
        distance = int(self.route.distance) or 0
        min_price = int(self.route.min_price)
        avg_price = int(self.route.avg_price)
        companies = ", ".join({t.company.name for t in self.route.trips.all()})

        data = {
            "title": f"Preguntas frecuentes sobre el viaje de {origin} a {dest}",
            "item": [
                # Price Q&A
                {
                    "question": f"¿Cuánto sale el pasaje de {origin} a {dest}?",
                    "answer": RichText(
                        f"<p>En promedio, el pasaje en micro está a unos <b>ARS {avg_price}</b>, pero podés conseguir lo más barato desde "
                        f"<b>ARS {min_price}</b>.</p><p>Acordate que el precio final depende de la empresa que elijas y el "
                        f"tipo de coche <em>(Común, Semi-Cama o Ejecutivo)</em>.</p><p>Un consejo: los precios suelen subir en fechas "
                        f"clave (como Semana Santa o fin de año), así que mejor organizate con tiempo.</p>"
                    ),
                },
                # Duration Q&A
                {
                    "question": f"¿Cuánto tiempo lleva el viaje de {origin} a {dest}?",
                    "answer": RichText(
                        f"<p>El viaje suele durar más o menos entre <b>{low_d}</b> y <b>{avg_d}</b>.</p><p>Eso sí, tené en cuenta que el viaje "
                        f"se puede alargar un poco dependiendo del tráfico para salir de la ciudad, cómo estén las rutas o si el micro "
                        f"es de los que paran mucho en el camino a alzar pasajeros.</p><p>Para que sepas la distancia entre "
                        f"<b>{origin}</b> y <b>{dest}</b> es de aproximadamente <b>{distance}</b> kilómetros</p>"
                    ),
                },
                # Empresas
                {
                    "question": f"¿Qué empresas de micro operan en la ruta {origin} - {dest}?",
                    "answer": RichText(
                        f"<p>Las principales empresas de micro que te llevan en esta ruta son <b>{companies}</b> entre otras. "
                        f"En <b>Ventanita</b> podés mirar bien los horarios de cada una para elegir la opción que mejor te guste.</p>"
                    ),
                },
                # First & last departure Q&A
                {
                    "question": f"¿Cuándo es la primera y la última salida de micro entre {origin} y {dest}?",
                    "answer": RichText(
                        f"<p>La primera salida de <b>{origin}</b> a <b>{dest}</b> sale a las <b>{self.route.first_departure:%I:%M %p}</b> "
                        f"y la última salida es a las <b>{self.route.last_departure:%I:%M %p}</b></p>"
                    ),
                },
                # Distance Q&A
                {
                    "question": f"¿Cuántos kilómetros hay de {origin} a {dest}?",
                    "answer": RichText(
                        f"<p>La distancia entre <b>{origin}</b> y <b>{dest}</b> es de aproximadamente <b>{distance}</b> kilómetros, "
                        f"aunque puede variar según el recorrido y los puntos de salida y llegada.</p> "
                        f"<p>Para que sepas el viaje suele durar más o menos entre <b>{low_d}</b> y <b>{avg_d}</b>.</p>"
                    ),
                },
                # Generic Bus categories
                {
                    "question": "¿Qué diferencia hay entre los servicios Común, Semi-Cama y Ejecutivo?",
                    "answer": RichText(
                        "<p>El servicio común realiza más paradas en el trayecto. Los servicios Semi-Cama y Ejecutivo "
                        "ofrecen asientos más reclinables, aire acondicionado, pantallas y, en algunos casos, refrigerios "
                        "a bordo, siendo ideales para viajar de noche.</p>"
                    ),
                },
                # Generic Advice
                {
                    "question": "¿Es necesario comprar los pasajes con anticipación?",
                    "answer": RichText(
                        "<p>Aunque haya mucha frecuencia, te recomendamos asegurar tu lugar con días de antelación "
                        "si planeás viajar durante el verano, fines de semana largos, Semana Santa o "
                        "fiestas de fin de año, ya que la demanda aumenta considerablemente.</p>"
                    ),
                },
                # Generic Documentation
                {
                    "question": "¿Qué documentación necesito para viajar en bus por Argentina?",
                    "answer": RichText(
                        "<p>Solo necesitás presentar tu <b>DNI</b> vigente al momento de abordar. "
                        "Si viajás con <b>menores</b> de edad, recordá llevar también el <b>Certificado de Nacimiento</b> o "
                        "la <i>autorización correspondiente</i> si no viaja con ambos padres.</p>"
                    ),
                },
                # Generic Equipaje
                {
                    "question": "¿Cuánto equipaje puedo llevar en el bus?",
                    "answer": RichText(
                        "<p>Tecnicamente podés subir con un bolso de mano chico <em>(de hasta 40x40x25 cm)</em> y llevar en la bodega "
                        "una maleta grande <em>(máximo 80x80x30 cm)</em>.</p><p>En total, tu equipaje no debe pasar los <b>15 kilos</b>. "
                        "Si te excedés en el peso o el tamaño, la empresa te puede cobrar una tasa extra basada en sus precios de encomiendas.</p> "
                        "<p>Pero en realidad no todas las empresas los tienen muy estricto esas reglas según las observaciones de los pasajeros.</p>"
                    ),
                },
            ],
        }
        return ("faq", data)

    def get_companies(self) -> tuple[str, dict]:
        origin = self.route.origin
        dest = self.route.destination
        companies = list({t.company for t in self.route.trips.all()})

        items = []
        for c in companies:
            try:
                page = PartnerPage.objects.get(slug=c.slug)
            except PartnerPage.DoesNotExist:
                self.danger(f"cant find page for {c.slug}")
            items.append({"title": c.name, "page": page})

        data = {
            "heading_text": f"Empresas que opera de {origin} a {dest}",
            "item": items,
        }
        return ("Links", data)

    def success(self, msg: str) -> str:
        self.stdout.write(self.style.SUCCESS(msg))

    def danger(self, msg: str) -> str:
        self.stdout.write(self.style.ERROR(msg))
