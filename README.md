Actividad 1:

Cuando ajustamos los límites inferior y superior del filtro de color (como los valores de `lower_red` y `upper_red` en HSV), estamos definiendo la "tolerancia" de lo que consideramos como el color rojo. 

Aquí tienes lo que ocurre en cada caso extremo:

### 1. ¿Qué ocurre cuando el rango es muy estrecho? (Poca tolerancia)
- **Sub-segmentación (Falsos Negativos):** El filtro se vuelve extremadamente estricto y solo deja pasar los tonos de rojo más "perfectos" o puros.
- **Consecuencia en la máscara:** Cualquier variación natural en el color de la fruta, así como las zonas con un poco de sombra, curvatura o reflejos de luz, quedarán fuera del rango. Las frutas aparecerán en la máscara incompletas, llenas de huecos, como si estuvieran "mordidas" o fragmentadas. En el peor de los casos, frutas enteras que estén bajo una iluminación ligeramente distinta desaparecerán por completo de la detección.

### 2. ¿Qué ocurre cuando el rango es muy amplio? (Mucha tolerancia)
- **Sobre-segmentación (Falsos Positivos):** El filtro se vuelve demasiado permisivo y empieza a aceptar colores que se parecen al rojo, pero que en realidad no lo son (por ejemplo, tonos naranjas, magentas, marrones claros o sombras cálidas).
- **Consecuencia en la máscara:** La máscara empezará a detectar partes del fondo, la mesa, o reflejos en otros objetos como si fueran frutas. En la imagen resultante verás enormes manchas blancas de "ruido" por todos lados, o incluso peor: los objetos que querías detectar se fusionarán con el fondo o con otros objetos cercanos formando un solo bloque blanco masivo, haciendo que sea imposible contar o separar las frutas reales. 

Encontrar el equilibrio perfecto en el rango HSV es la clave para que la máscara cubra la totalidad de la fruta (sin huecos) y excluya todo lo que pertenece al fondo (sin ruido).

Actividad 2:

Al procesar una imagen usando segmentación de color (como hicimos con el rango HSV), generalmente nos encontramos con dos tipos principales de ruido:

1. **Ruido de fondo (Falsos Positivos):** En la máscara original verás pequeños "puntitos" o manchitas blancas aisladas en áreas donde no hay frutas. Esto ocurre porque la iluminación del entorno, ciertas sombras o pequeños reflejos en otros objetos accidentalmente tienen tonalidades que caen dentro del rango de color rojo que definimos.
2. **Huecos en el objeto (Falsos Negativos):** Dentro de las manchas blancas grandes (que son las frutas), pueden aparecer pequeños huecos o píxeles negros. Esto suele ser provocado por el reflejo intenso de la luz en la superficie brillante de la fruta (lo que hace que ese punto se vea casi blanco, saliéndose de nuestro rango rojo) o por sombras muy oscuras.

**¿Por qué es estrictamente necesario eliminar este ruido antes del conteo?**

El paso que le sigue a obtener una máscara suele ser utilizar una función (como `cv2.findContours` en OpenCV) que busca y rodea todas las agrupaciones de píxeles blancos conectados. 

- **Si no eliminas el ruido de fondo:** El algoritmo va a encontrar esos puntitos blancos aislados flotando en el fondo y contará cada uno de ellos como si fuera una fruta adicional, lo cual hará que tu conteo total sea excesivo y erróneo.
- **Si no cierras los huecos en las frutas:** El algoritmo podría confundirse al trazar el borde, interpretando una sola fruta que tiene un "agujero negro" en medio como si en realidad fueran dos o más contornos diferentes (fragmentando el objeto), o arruinando el cálculo del área y del centro de la fruta.

Aplicando la **Apertura** (que borra los puntitos sueltos del fondo) y el **Cierre** (que rellena los huecos en la fruta), te aseguras de que en la máscara quede un solo bloque sólido y limpio de color blanco por cada fruta real, lo que garantiza que tu algoritmo cuente 1 bloque = 1 fruta con total precisión.

Aquí tienes las respuestas a esas preguntas, redactadas de manera clara para que puedas integrarlas directamente en tu reporte o archivo `ReadMe.md`:

### 1. ¿Qué color fue más fácil segmentar y cuál presentó más ruido? ¿Por qué?
Generalmente, el **color rojo o el verde son los más fáciles de segmentar** en este tipo de ejercicios, mientras que el **color amarillo suele presentar mucho más ruido**.
* **¿Por qué?** El color amarillo se encuentra en un rango de matiz muy estrecho que colinda con el naranja y el café (que es básicamente un amarillo/naranja con poco brillo). Si en la imagen hay sombras cálidas, una mesa de madera o luces amarillentas, la cámara capta esos píxeles con un matiz similar al de la fruta. Por el contrario, los rojos puros o verdes suelen contrastar mucho mejor con los fondos neutros, lo que reduce la aparición de falsos positivos (ruido).

### 2. ¿Por qué HSV es más adecuado que RGB para esta tarea?
En el modelo **RGB** (Rojo, Verde, Azul), la información del color y la iluminación están fuertemente mezcladas. Si una fruta está en la sombra, sus tres valores (R, G, B) cambian drásticamente, lo que hace casi imposible definir un solo rango numérico para "el color de la fruta".
El modelo **HSV** (Matiz, Saturación, Valor) separa la "luz" del "color real":
* **H (Hue/Matiz):** Contiene el color puro (qué tan rojo, verde o amarillo es).
* **S y V (Saturación y Valor):** Manejan la intensidad del color y la cantidad de luz.
Gracias a esta separación, en HSV puedes decirle al programa: *"Busca este color exacto (H), sin importar si está un poco oscuro por una sombra (V) o un poco deslavado (S)"*.

### 3. ¿Cómo afecta la iluminación al canal V?
El canal **V (Valor o Brillo)** representa la cantidad de luz o la intensidad luminosa del píxel.
Si la iluminación de la habitación cambia (por ejemplo, se nubla o se enciende un flash), el canal V subirá o bajará drásticamente. Las partes de la fruta donde pega la luz directamente tendrán un valor de **V muy alto** (acercándose a 255), mientras que las partes de la fruta que están en la sombra tendrán un valor de **V muy bajo**. Afortunadamente, como el matiz (canal H) se mantiene casi igual, el filtro HSV sigue funcionando incluso si V fluctúa.

### 4. ¿Qué sucede si dos frutas distintas tienen tonos similares?
Si una manzana y una fresa tienen exactamente el mismo tono de rojo, **el algoritmo las detectará a ambas por igual y las unirá en la misma máscara**. 
La segmentación por color es *"ciega"* a la forma del objeto; si los valores de los píxeles de ambas frutas caen dentro del mismo rango HSV, el programa no tiene forma de saber que son frutas de especies diferentes.

### 5. ¿Qué limitaciones tiene la segmentación por color?
La segmentación por color es muy rápida y efectiva en condiciones controladas, pero tiene grandes limitaciones en el mundo real:
* **Dependencia extrema de la iluminación:** Si la luz cambia de blanca (luz de día) a amarilla (foco de casa), los colores de toda la imagen cambian y los rangos definidos dejarán de funcionar.
* **Incapacidad para distinguir formas:** Como se mencionó, agrupará objetos diferentes si comparten color.
* **Problemas con fondos del mismo color:** Si pones una manzana verde sobre un mantel verde o pasto, la segmentación fallará por completo al no poder separar la fruta de su entorno.
* **Problemas de superposición (Oclusión):** Si dos frutas del mismo color están tocándose, la máscara resultante será un solo bloque blanco masivo. La computadora contará "1 objeto gigante" en lugar de 2 frutas separadas, a menos que se apliquen algoritmos geométricos mucho más avanzados (como el algoritmo *Watershed*).


Tabla comparativa:

| Color   | Número de frutas detectadas | Observaciones |
