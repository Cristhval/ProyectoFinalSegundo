# ProyectoFinalSegundo

# API Menuboard
Para el proyecto, se decidió usar dos APIs públicas, las cuales son:

# PokéAPI
Esta API gratuita proporciona información sobre el universo de Pokémon y permite acceder a diversos datos del mismo.
El propósito de utilizar esta API en el proyecto es generar Pokémon aleatorios, los cuales estarán asociados a un producto llamado Cajita Feliz.
Con la compra de una Cajita Feliz, se entregará un Pokémon aleatorio, lo que hace que el producto sea más atractivo para los clientes.

Sus funcionalidades principales son: 

- Obtener información de cualquier Pokémon por nombre o ID. 

- Generar un Pokémon aleatorio a partir del total disponible en la API.

Requisitos: 

- No requiere autenticación con API Key, por lo que cualquier usuario puede hacer solicitudes.

- Usa el formato JSON para las respuestas.

- Se accede mediante métodos HTTP GET.

Limitaciones: 

- Límite de 100 solicitudes por minuto en la versión gratuita.

- No tiene datos sobre los Pokémon de última generación de forma inmediata tras su lanzamiento.

- No ofrece imágenes de alta resolución, solo sprites oficiales.

![img_1.png](img_1.png) 
![img_2.png](img_2.png) 


# OpenWeatherMap
Este es un servicio que proporciona datos meteorológicos en tiempo real y suele utilizarse en aplicaciones web y móviles para obtener información climática.
La API es gratuita, aunque también cuenta con una versión de pago.

Sus funcionalidades principales son: 

- Obtener el clima actual de cualquier ciudad por nombre o coordenadas.

Acceder a datos como:

    - Temperatura, humedad y presión atmosférica.

    - Velocidad y dirección del viento.

    - Condiciones meteorológicas (lluvia, nieve, nubes, etc.).

    - Hora de salida y puesta del sol.

- Consultar pronósticos de hasta 16 días.

- Alertas meteorológicas para eventos extremos.

Requisitos: 

- Se requiere una API Key (se obtiene registrándose en OpenWeatherMap).

- Las respuestas se entregan en formato JSON.

- Uso de métodos HTTP GET para las solicitudes.

Limitaciones: 

- En la versión gratuita: 

    - Se permite un máximo de 60 solicitudes por minuto.
  
    - No incluye datos avanzados como calidad del aire o información histórica.
  
    - El acceso a datos de clima en alta resolución está limitado a los planes pagos.

- En ocasiones, la información del clima puede tener un retraso de 5 a 10 minutos.

El propósito de integrarla al proyecto es ofrecer promociones basadas en el clima actual.
Por ejemplo:

- Si el clima es lluvioso, se ofrecerán descuentos en comidas calientes.

- Si el día es caluroso, se ofrecerán descuentos en helados o bebidas frías. 

![img.png](img.png) 
![img_3.png](img_3.png)