# Ejemplos de CURL para probar el endpoint `/api/costos/calcular`

## Endpoint
```
POST https://carga-horas-backend.onrender.com/api/costos/calcular
```

## Formato de datos esperado

El endpoint acepta una lista de objetos con el siguiente formato:

```json
[
    {
        "tareaId": "string (UUID)",
        "recursoId": "string (UUID)",
        "periodos": [
            {
                "anio": 2025,
                "mes": 11,
                "horas_aprobadas": 8.0
            }
        ]
    }
]
```

## Ejemplo 1: Curl simple con datos mínimos

```bash
curl -X POST "https://carga-horas-backend.onrender.com/api/costos/calcular" \
  -H "Content-Type: application/json" \
  -d '[
    {
        "tareaId": "b635b4ca-c091-472c-8b5a-cb3086d1973",
        "recursoId": "2e6ecd47-fa18-490e-b25a-c9101a398b6d",
        "periodos": [
            {
                "anio": 2025,
                "mes": 11,
                "horas_aprobadas": 8.0
            }
        ]
    }
]'
```

## Ejemplo 2: Curl con múltiples periodos

```bash
curl -X POST "https://carga-horas-backend.onrender.com/api/costos/calcular" \
  -H "Content-Type: application/json" \
  -d '[
    {
        "tareaId": "b635b4ca-c091-472c-8b5a-cb3086d1973",
        "recursoId": "2e6ecd47-fa18-490e-b25a-c9101a398b6d",
        "periodos": [
            {
                "anio": 2025,
                "mes": 9,
                "horas_aprobadas": 8.0
            },
            {
                "anio": 2025,
                "mes": 10,
                "horas_aprobadas": 13.5
            },
            {
                "anio": 2025,
                "mes": 11,
                "horas_aprobadas": 22.0
            }
        ]
    }
]'
```

## Ejemplo 3: Curl con datos reales (obtenidos del endpoint `/api/horas-aprobadas`)

```bash
# Primero obtener las horas aprobadas
HORAS=$(curl -s "https://carga-horas-backend.onrender.com/api/horas-aprobadas")

# Luego enviarlas al endpoint de cálculo de costos
curl -X POST "https://carga-horas-backend.onrender.com/api/costos/calcular" \
  -H "Content-Type: application/json" \
  -d "$HORAS"
```

## Ejemplo 4: Curl con formato legible (usando jq para formatear)

```bash
curl -X POST "https://carga-horas-backend.onrender.com/api/costos/calcular" \
  -H "Content-Type: application/json" \
  -d '[
    {
        "tareaId": "b635b4ca-c091-472c-8b5a-cb3086d1973",
        "recursoId": "2e6ecd47-fa18-490e-b25a-c9101a398b6d",
        "periodos": [
            {
                "anio": 2025,
                "mes": 11,
                "horas_aprobadas": 8.0
            }
        ]
    }
]' | python3 -m json.tool
```

## Ejemplo 5: Curl con verbose para debugging

```bash
curl -v -X POST "https://carga-horas-backend.onrender.com/api/costos/calcular" \
  -H "Content-Type: application/json" \
  -d '[
    {
        "tareaId": "b635b4ca-c091-472c-8b5a-cb3086d1973",
        "recursoId": "2e6ecd47-fa18-490e-b25a-c9101a398b6d",
        "periodos": [
            {
                "anio": 2025,
                "mes": 11,
                "horas_aprobadas": 8.0
            }
        ]
    }
]'
```

## Notas importantes

1. **El endpoint acepta el body como lista directamente** (formato recomendado)
2. **También acepta el body envuelto en un objeto** con las claves `horas_aprobadas` o `data`
3. **El endpoint actúa como proxy** hacia el módulo de finanzas configurado en `FINANZAS_API_URL`
4. **Si `USE_FINANZAS_MOCK=true`**, el endpoint usará datos mock en lugar de llamar al módulo real
5. **CORS está configurado** para aceptar requests desde cualquier origen

## Respuesta esperada

El endpoint retorna una lista de objetos con el costo por hora para cada rol:

```json
[
    {
        "rolId": "uuid-del-rol",
        "costoPorHora": 50.0
    }
]
```

## Endpoint relacionado: Obtener horas aprobadas

Para obtener las horas aprobadas que se deben enviar al endpoint de costos:

```bash
curl -s "https://carga-horas-backend.onrender.com/api/horas-aprobadas" | python3 -m json.tool
```

