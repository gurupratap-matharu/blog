from django.db import models


class Province(models.TextChoices):
    BUENOSAIRES = "BUE", "Buenos Aires"
    CATAMARCA = "CAT", "Catamarca"
    CHACO = "CHA", "Chaco"
    CHUBUT = "CHU", "Chubut"
    CORDOBA = "COR", "Córdoba"
    CORRIENTES = "CRR", "Corrientes"
    ENTRERIOS = "ENT", "Entre Ríos"
    FORMOSA = "FOR", "Formosa"
    JUJUY = "JUY", "Jujuy"
    LAPAMPA = "LAP", "La Pampa"
    LARIOJA = "LAR", "La Rioja"
    MENDOZA = "MZA", "Mendoza"
    MISIONES = "MIS", "Misiones"
    NEUQUEN = "NEQ", "Neuquén"
    RIONEGRO = "RNG", "Río Negro"
    SALTA = "SAL", "Salta"
    SANJUAN = "SJU", "San Juan"
    SANLUIS = "SLU", "San Luis"
    SANTACRUZ = "SCR", "Santa Cruz"
    SANTAFE = "SFE", "Santa Fe"
    SANTIAGODELESTERO = "SDE", "Santiago Del Estero"
    TIERRADELFUEGO = "TDF", "Tierra Del Fuego"
    TUCUMAN = "TUC", "Tucumán"


class Country(models.TextChoices):
    ARGENTINA = "ARG", "Argentina"
    BOLIVIA = "BOL", "Bolivia"
    BRAZIL = "BRA", "Brasil"
    CHILE = "CHL", "Chile"
    PARAGUAY = "PGY", "Paraguay"
    PERU = "PER", "Perú"
    URUGUAY = "URU", "Uruguay"
