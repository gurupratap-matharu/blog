START_SESSION_XML = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope
xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><StartSessionResponse
xmlns="http://tempuri.org/"><StartSessionResult><NewDataSet
xmlns=""><SessionInformation><ConnectionId>{connection_id}</ConnectionId></SessionInformation><Result><IsOk>true</IsOk><HasWarnings>false</HasWarnings></Result></NewDataSet></StartSessionResult></StartSessionResponse></soap:Body></soap:Envelope>"""

GET_BY_FECHA_ORIGEN_DESTINO_XML = """<?xml version="1.0"?>
<Resultado xmlns="" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" Desde="393"
Hasta="443" Fecha="12-05-2025">
  <Servicio idServicio="1">
    <CodigoServicio>BRA2</CodigoServicio>
    <HoraSalida>12-05-2025 06:00</HoraSalida>
    <HoraLlegada>12-05-2025 09:20</HoraLlegada>
    <ButacasLibres>03 20</ButacasLibres>
    <EmpresaId>95</EmpresaId>
    <Precio>03 550044.00</Precio>
    <Clase>03</Clase>
    <EsInternacional>0</EsInternacional>
    <VeTaquilla>1</VeTaquilla>
    <Empresa>GOQ</Empresa>
    <FechaOrigen>11-05-2025 05:00</FechaOrigen>
    <EmpresaTransportista>GOQ</EmpresaTransportista>
    <EmpresaTransportistaId>95</EmpresaTransportistaId>
    <Prom xml:space="preserve"> </Prom>
    <RG3450>03 0.00</RG3450>
    <SPDPax/>
    <Moneda>$</Moneda>
    <TarifaPromo>03 550044.00</TarifaPromo>
    <TasaEmbarque>0.00</TasaEmbarque>
    <TasaEmbarqueTipo/>
    <TasaEmbarqueTipoId>0</TasaEmbarqueTipoId>
    <NacionalidadObligatoria>1</NacionalidadObligatoria>
    <MonedaISO>ARS</MonedaISO>
    <TieneDescuento>*</TieneDescuento>
  </Servicio>
</Resultado>"""


SERVICE = {
    "result": {"is_ok": "true", "has_warnings": "false"},
    "stops": {
        "origin": "Gualeguaychú {GUALEGUAYCHU - ENTRE RÍOS}",
        "origin_address": "Av Costanera y Rivera",
        "destination": "2 - Retiro - RRO {Ciudad Autonoma de Buenos Aires - CAPITAL FEDERAL}",
        "destination_address": "Avenida Antartida Argentina y Calle 10",
    },
    "service": {
        "company": "GOQ",
        "departure": "2025-05-14T06:00:00-03:00",
        "arrival": "2025-05-14T09:20:00-03:00",
    },
    "floors": {"name": "A", "title": "Piso: A", "rows": "5", "cols": "5"},
    "qualities": {"code": "03", "description": "Calidad 03"},
    "seats": [
        {
            "floor": "A",
            "row": "1",
            "col": "1",
            "label": "1",
            "quality": "03",
            "status": "Free",
            "is_selectable": "true",
            "category": "Seat",
        },
        {
            "floor": "A",
            "row": "1",
            "col": "2",
            "label": "2",
            "quality": "03",
            "status": "Free",
            "is_selectable": "true",
            "category": "Seat",
        },
        {
            "floor": "A",
            "row": "1",
            "col": "3",
            "label": "TV",
            "quality": "03",
            "status": "Undefined",
            "is_selectable": "false",
            "category": "TV",
        },
        {
            "floor": "A",
            "row": "1",
            "col": "4",
            "label": "3",
            "quality": "03",
            "status": "Free",
            "is_selectable": "true",
            "category": "Seat",
        },
        {
            "floor": "A",
            "row": "1",
            "col": "5",
            "label": "4",
            "quality": "03",
            "status": "Free",
            "is_selectable": "true",
            "category": "Seat",
        },
    ],
}

STOPS = [
    {
        "id": "Gua",
        "name": "Gualeguaychu",
        "state": "Entre Ríos",
        "country": "Argentina",
        "arrival": "06:00",
        "departure": "06:00",
    },
    {
        "id": "Rro",
        "name": "Ciudad Autonoma De Buenos Aires",
        "state": "Capital Federal",
        "country": "Argentina",
        "arrival": "09:20",
        "departure": "09:20",
    },
]
