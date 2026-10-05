"""Contenido del juego "Garage → Imperio" (parodia académica, inspirada libremente en Apple).

Sigue el contrato descrito en el docstring de liderar/engine.py.
Los nombres de personajes y empresas están alterados a propósito (Aple, Macrosoft, etc.).
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Personajes (retratos procedurales)
# ---------------------------------------------------------------------------
CHARACTERS = {
    "nash": {"name": "Profe Nash", "role": "Mentor y teórico de juegos",
             "skin": (230, 190, 160), "hair": (200, 200, 205), "shirt": (70, 100, 150),
             "accessory": "glasses"},
    "woz": {"name": "Steve Wozniac", "role": "Socio ingeniero",
            "skin": (235, 200, 170), "hair": (110, 75, 45), "shirt": (90, 150, 110),
            "accessory": "beard"},
    "mike": {"name": "Mike Markula", "role": "Inversionista ángel",
             "skin": (225, 180, 150), "hair": (60, 50, 45), "shirt": (60, 60, 80),
             "accessory": "tie"},
    "bill": {"name": "Bill Gatez", "role": "CEO de Macrosoft",
             "skin": (240, 205, 180), "hair": (150, 110, 70), "shirt": (150, 160, 175),
             "accessory": "glasses"},
    "scully": {"name": "John Scully", "role": "CEO contratado",
               "skin": (232, 195, 165), "hair": (90, 90, 95), "shirt": (40, 50, 70),
               "accessory": "tie"},
    "mosk": {"name": "Elon Mosk", "role": "Magnate de cohetes y autos",
             "skin": (228, 190, 160), "hair": (45, 35, 30), "shirt": (25, 25, 30),
             "accessory": "none"},
    "ana": {"name": "Ana Byte", "role": "Ingeniera del equipo",
            "skin": (200, 150, 115), "hair": (30, 20, 25), "shirt": (180, 90, 140),
            "accessory": "glasses"},
    "beto": {"name": "Beto Debug", "role": "Programador del equipo",
             "skin": (215, 170, 135), "hair": (140, 90, 40), "shirt": (200, 120, 50),
             "accessory": "cap"},
    "pepe": {"name": "Pepe Pixel", "role": "Diseñador del equipo",
             "skin": (190, 140, 105), "hair": (20, 20, 25), "shirt": (120, 70, 170),
             "accessory": "turtleneck"},
    "prensa": {"name": "Lola Titular", "role": "Periodista tecnológica",
               "skin": (235, 195, 170), "hair": (170, 60, 40), "shirt": (200, 60, 70),
               "accessory": "none"},
    "junta": {"name": "La Junta", "role": "Directorio de Aple",
              "skin": (225, 185, 155), "hair": (170, 170, 175), "shirt": (50, 50, 55),
              "accessory": "tie"},
    "tu": {"name": "Tú", "role": "Fundador de Aple",
           "skin": (225, 185, 155), "hair": (40, 30, 25), "shirt": (30, 30, 35),
           "accessory": "turtleneck"},
}


def ch(text, effects, feedback, concept=None, requires=None):
    d = {"text": text, "effects": effects, "feedback": feedback}
    if concept:
        d["concept"] = concept
    if requires:
        d["requires"] = requires
    return d


def story(speaker, portrait, text, choices, requires=None):
    d = {"type": "story", "speaker": speaker, "portrait": portrait, "text": text,
         "choices": choices}
    if requires:
        d["requires"] = requires
    return d


W, M, N = "Steve Wozniac", "Mike Markula", "Profe Nash"
B, S, E = "Bill Gatez", "John Scully", "Elon Mosk"

# ---------------------------------------------------------------------------
# Capítulos
# ---------------------------------------------------------------------------
CHAPTERS = []

# ===== 1. El garaje: estilos de liderazgo =====
CHAPTERS.append({
    "id": "garaje",
    "title": "Capítulo 1 · El garaje",
    "concept": "Estilos de liderazgo",
    "lesson": ("Los estilos de liderazgo (Lewin; Bass) describen cómo se decide y se motiva: "
               "el autocrático decide solo, el democrático decide con el equipo, el laissez-faire "
               "delega por completo, el transformacional inspira con una visión y el transaccional "
               "intercambia premios por resultados. No hay un estilo universal: depende de la "
               "madurez del equipo y de la situación (liderazgo situacional)."),
    "scenes": [
        story("Narrador", "nash",
              "1976. Un garaje, soldadores prestados y una idea: computadoras personales. Tu socio "
              "Steve Wozniac ya tiene un prototipo. Antes de nada, el equipo necesita saber cómo "
              "piensas liderar.",
              [ch("Escuchar con atención", {"morale": 2},
                  "Empezar escuchando genera confianza y da información valiosa al líder.",
                  "Escucha activa"),
               ch("Hablar yo primero y marcar el rumbo", {"morale": -2, "progress": 2},
                  "Marcar el rumbo da claridad, pero hablar antes de escuchar limita la información.",
                  "Comunicación")]),
        {"type": "leader",
         "text": "¿Qué tipo de líder serás? Tu estilo modificará cómo te afectan las decisiones "
                 "durante todo el juego."},
        story(W, "woz",
              "Woz: 'Terminé la placa, pero el chip de video tiene dos diseños posibles. Uno es "
              "barato y probado; el otro es genial y arriesgado. Tú mandas.'",
              [ch("Decidir yo solo: el probado", {"progress": 4, "morale": -3, "cash": 2000},
                  "Decisión rápida y sin debate: avanza el producto, pero Woz se siente ignorado.",
                  "Estilo autocrático"),
               ch("Votar entre todos", {"morale": 2, "progress": 2, "innovation": 2},
                  "La participación sube la moral y mejora la idea, aunque el proceso es lento.",
                  "Estilo democrático"),
               ch("Dejar que Woz elija lo que quiera", {"innovation": 4, "progress": 2, "morale": 2},
                  "Con un experto motivado, delegar libera creatividad; sin supervisión, hay riesgo.",
                  "Laissez-faire"),
               ch("Pintar la visión: 'cambiaremos el mundo' y elegir el genial",
                  {"innovation": 5, "morale": 2, "reputation": 2, "cash": -2000},
                  "Una visión inspiradora motiva más allá del sueldo, pero cuesta dinero.",
                  "Liderazgo transformacional", {"style": "transformacional"}),
               ch("Pactar un bono por entregar el chip a tiempo",
                  {"progress": 5, "morale": 2, "cash": -1500, "power.recompensa": 5},
                  "Un intercambio claro de premio por resultado es eficiente, pero poco inspirador.",
                  "Liderazgo transaccional", {"style": "transaccional"})]),
        story(M, "mike",
              "Mike Markula llega al garaje con un maletín. 'Veo potencial. Pongo capital si me "
              "convences de que sabes liderar. ¿Cómo quieres que sea tu equipo?'",
              [ch("Una jerarquía clara y yo al mando", {"cash": 8000, "morale": -2, "power.legitimo": 5},
                  "Mike valora el orden y financia; el mando firme da seguridad al inversor.",
                  "Poder legítimo"),
               ch("Un equipo autogestionado de expertos", {"cash": 5000, "innovation": 2, "power.experto": 5},
                  "Confías en la competencia técnica; el inversor ve talento, aunque falta estructura.",
                  "Poder experto"),
               ch("Una visión tan magnética que todos quieren seguirla",
                  {"cash": 11000, "reputation": 2, "power.referente": 6},
                  "El carisma convence: tu influencia se basa en la admiración, no en el cargo.",
                  "Poder referente", {"style": "transformacional"}),
               ch("Pedirle más dinero sin dar explicaciones", {"cash": 3000, "reputation": -6},
                  "Pedir sin justificar daña la credibilidad; el inversor desconfía.",
                  "Comunicación")]),
        story("Narrador", "nash",
              "Primera demo ante el club de aficionados. El prototipo se cuelga a los diez minutos. "
              "El público mira. Tu equipo mira. Todos esperan tu reacción.",
              [ch("Asumir la culpa y pedir tiempo al público", {"reputation": 2, "morale": 2},
                  "Asumir responsabilidad refuerza la confianza y protege la moral del equipo.",
                  "Responsabilidad"),
               ch("Gritarle a Woz delante de todos", {"morale": -12, "reputation": -4},
                  "Humillar en público destruye la moral; el autoritarismo mal usado sale caro.",
                  "Clima laboral"),
               ch("Improvisar: mostrar el diseño en pizarra y vender la visión",
                  {"innovation": 2, "reputation": 2, "progress": 2},
                  "Convertir un fallo en una oportunidad demuestra liderazgo adaptable.",
                  "Liderazgo situacional")]),
    ],
})

# ===== 2. Armando el equipo =====
CHAPTERS.append({
    "id": "equipo",
    "title": "Capítulo 2 · Armando el equipo",
    "concept": "Gestión de personal y presupuesto",
    "lesson": ("Gestionar personas implica equilibrar competencia, motivación y costo. "
               "La nómina es un costo fijo recurrente: contratar más no siempre es mejor. "
               "Delegar con claridad (qué, quién, hasta cuándo) y resolver conflictos "
               "tempranamente evita pérdidas de productividad."),
    "scenes": [
        story(M, "mike",
              "Mike revisa tu hoja de cálculo: 'Con lo que hay en caja puedes contratar, pero la "
              "nómina se paga cada mes. Contratar de más es la forma más rápida de quebrar.'",
              [ch("Prometer que cuidaré el presupuesto", {"reputation": 2},
                  "Mostrar disciplina financiera da confianza a quienes aportan capital.",
                  "Presupuesto"),
               ch("Contratar a todo el que pueda, ya veremos cómo pagar", {"progress": 2, "cash": -3000, "reputation": -3},
                  "Sin control de costos, la nómina futura compromete la caja.",
                  "Costos fijos")]),
        {"type": "hire", "text": "Llegan seis candidatos al garaje. Puedes contratar hasta tres. "
                                 "Ojo con el sueldo: se descuenta hoy y cada fin de capítulo.",
         "max_hires": 3,
         "candidates": [
             {"name": "Ada Lovelass", "role": "Ingeniera de software", "skill": 9, "salary": 9000,
              "trait": "Genio absoluto. Cobra como un cohete."},
             {"name": "Linus Torbaldos", "role": "Programador de sistemas", "skill": 8, "salary": 7000,
              "trait": "Código impecable, modales de erizo."},
             {"name": "Pepe Pixel", "role": "Diseñador", "skill": 6, "salary": 4500,
              "trait": "Cambia de tipografía cada hora."},
             {"name": "Beto Debug", "role": "Becario", "skill": 3, "salary": 2000,
              "trait": "Aprende rápido... y rompe más rápido."},
             {"name": "Carla Cuentas", "role": "Contadora", "skill": 5, "salary": 3500,
              "trait": "Tus gastos le quitan el sueño."},
             {"name": "Nico Networking", "role": "Vendedor", "skill": 6, "salary": 5000,
              "trait": "Vendería hielo a los pingüinos."}]},
        story("Ana Byte", "ana",
              "Ana: 'Pepe quiere rediseñar la carcasa por quinta vez y Beto ya no le habla. Esto "
              "frena la entrega. ¿Qué haces?'",
              [ch("Reunirlos y acordar reglas y plazos de rediseño", {"morale": 2, "progress": 2},
                  "Mediar con reglas claras resuelve el conflicto de raíz y recupera productividad.",
                  "Resolución de conflictos"),
               ch("Ignorarlo: que se arreglen entre ellos", {"morale": -8, "progress": -4},
                  "Evitar el conflicto lo agrava; se pierde tiempo y confianza.",
                  "Conflicto"),
               ch("Imponer mi decisión y cortar el debate", {"progress": 2, "morale": -5},
                  "Zanja el tema rápido, pero deja resentimiento: solución a corto plazo.",
                  "Estilo autocrático"),
               ch("Prometer un bono al que cumpla el plazo", {"progress": 2, "cash": -3000, "morale": 2},
                  "Un incentivo alinea intereses, aunque cuesta dinero y no resuelve la relación.",
                  "Recompensa")]),
        story("Ana Byte", "ana",
              "Ana pide autonomía para llevar el módulo de memoria completo. 'Dame el objetivo, "
              "no la receta.' Tú ya tienes el 80 % del diseño en la cabeza.",
              [ch("Delegar el módulo con objetivo y fecha clara", {"progress": 2, "morale": 2},
                  "Delegar con metas claras amplía capacidad del equipo y motiva a las personas.",
                  "Delegación"),
               ch("Quedarme con todo: nadie lo hace como yo", {"progress": 2, "morale": -8},
                  "El micromanagement te satura y desmotiva; no escala con el crecimiento.",
                  "Micromanagement"),
               ch("Delegar sin explicar nada", {"progress": -2, "innovation": 2, "morale": -2},
                  "Delegar sin claridad genera confusión: se necesita rol, meta y plazo.",
                  "Delegación")]),
        story("Carla Cuentas", "ana",
              "Llegan las facturas del mes: componentes, alquiler del garaje y pizza (mucha pizza). "
              "La caja se ve apretada. Es momento de decidir el rumbo financiero.",
              [ch("Recortar gastos no esenciales y renegociar con proveedores", {"cash": 5000, "morale": -2},
                  "Controlar costos mejora la liquidez sin tocar a las personas clave.",
                  "Control presupuestario"),
               ch("Pedir un adelanto a clientes con preventa", {"cash": 8000, "reputation": -3, "progress": -2},
                  "Una preventa da liquidez, pero compromete entregas futuras: riesgo de reputación.",
                  "Flujo de caja"),
               ch("Gastar en una oficina elegante para impresionar", {"cash": -9000, "reputation": 2},
                  "La imagen ayuda, pero el gasto fijo quema caja antes de tener ventas.",
                  "Gasto fijo")]),
    ],
})

# ===== 3. El proyecto Aple II =====
CHAPTERS.append({
    "id": "proyecto",
    "title": "Capítulo 3 · El proyecto Aple II",
    "concept": "Gestión de proyectos: triángulo de restricciones",
    "lesson": ("El triángulo de restricciones (alcance, tiempo y costo) indica que no se puede "
               "maximizar los tres a la vez: mover uno afecta a los otros y a la calidad. "
               "Gestionar riesgos consiste en anticiparlos, mitigarlos y negociar cambios de "
               "alcance formalmente, evitando el 'scope creep' y el 'crunch' permanente."),
    "scenes": [
        story("Narrador", "nash",
              "El Aple II será el primer ordenador personal con carcasa, color y teclado serio. "
              "Hay una feria en tres meses. Un proyecto serio necesita equilibrar tres fuerzas.",
              [ch("Definir alcance, plazo y presupuesto por escrito", {"progress": 2, "reputation": 2},
                  "Documentar las restricciones alinea expectativas y facilita el control del proyecto.",
                  "Planificación"),
               ch("Empezar a programar ya, planificar es perder tiempo", {"progress": 2, "morale": 2, "cash": -2000},
                  "Sin plan, el proyecto avanza rápido al principio pero se desvía luego.",
                  "Improvisación")]),
        {"type": "allocate",
         "text": "Reparte 6 puntos de esfuerzo entre alcance (más funciones), velocidad (llegar a "
                 "tiempo) y economía (ahorrar costos). No puedes maximizar los tres.",
         "points": 6,
         "slots": [
             {"key": "alcance", "label": "Alcance (más funciones)",
              "effects_per_point": {"innovation": 2, "progress": 1, "cash": -1000, "morale": -1}},
             {"key": "tiempo", "label": "Tiempo (entrega rápida)",
              "effects_per_point": {"progress": 2, "reputation": 1, "morale": -2, "cash": -500}},
             {"key": "costo", "label": "Costo (ahorro)",
              "effects_per_point": {"cash": 2000, "morale": 1, "innovation": -1, "progress": 1}}]},
        story("Ana Byte", "ana",
              "A tres semanas de la feria, el módulo de video acumula un retraso. Ana avisa: 'O nos "
              "matamos trabajando de noche, o pedimos más plazo.'",
              [ch("Crunch: noches y fines de semana", {"progress": 4, "morale": -14, "cash": -1000},
                  "Acelera el avance, pero el agotamiento baja la calidad y sube la rotación.",
                  "Crunch"),
               ch("Renegociar el plazo con transparencia", {"progress": 2, "morale": 2, "reputation": 2},
                  "Avisar riesgos a tiempo cuida la calidad y la confianza de los interesados.",
                  "Gestión de riesgos"),
               ch("Recortar funciones no esenciales", {"progress": 2, "innovation": -4, "cash": 2000},
                  "Reducir el alcance protege tiempo y costo (priorización tipo MVP).",
                  "Priorización"),
               ch("Fingir que todo va bien", {"reputation": -8, "morale": -4},
                  "Ocultar riesgos los vuelve crisis; los interesados pierden la confianza.",
                  "Comunicación de riesgos")]),
        story("Pepe Pixel", "pepe",
              "Pepe propone sumar una pantalla en colores y un parlante para la feria. 'Lo pidió "
              "un cliente, será rápido, ¡lo prometo!' (Nunca es rápido.)",
              [ch("Aceptar sin evaluar: el cliente manda", {"innovation": 2, "progress": -6, "cash": -4000},
                  "Es 'scope creep': añadir alcance sin control de cambios rompe plazos y presupuesto.",
                  "Scope creep"),
               ch("Evaluar el impacto y planificarlo para la versión 2", {"reputation": 2, "morale": 2, "progress": 2},
                  "Un control formal de cambios mantiene el proyecto bajo control.",
                  "Gestión de cambios"),
               ch("Rechazarlo de plano", {"morale": -4, "progress": 2, "innovation": -2},
                  "Evita el desvío, pero sin explicación puede frustrar a un buen talento.",
                  "Alcance")]),
        story("Lola Titular", "prensa",
              "La periodista Lola Titular visita el stand: '¿Cómo definirías el éxito del "
              "Aple II? Mi columna sale mañana.'",
              [ch("Producto de calidad, a tiempo y dentro del presupuesto", {"reputation": 2, "progress": 2},
                  "Un mensaje que equilibra las tres restricciones demuestra madurez en gestión.",
                  "Calidad y proyecto"),
               ch("Prometer revolucionar el mundo", {"reputation": 2, "innovation": 2, "progress": -3},
                  "Una promesa audaz atrae atención pero sube las expectativas del proyecto.",
                  "Expectativas"),
               ch("Evadir la pregunta", {"reputation": -3},
                  "La opacidad con la prensa desaprovecha una oportunidad de posicionamiento.",
                  "Stakeholders")]),
    ],
})

# ===== 4. Guerra de precios: teoría de juegos =====
CHAPTERS.append({
    "id": "guerra",
    "title": "Capítulo 4 · Guerra de precios",
    "concept": "Teoría de juegos: dilema del prisionero y equilibrio de Nash",
    "lesson": ("Un juego tiene jugadores, estrategias y pagos. En el dilema del prisionero, la "
               "estrategia dominante de cada jugador (traicionar) lleva a un equilibrio de Nash "
               "que es peor para ambos que cooperar. En juegos repetidos, estrategias como "
               "'ojo por ojo' (tit for tat) o 'grim trigger' permiten sostener la cooperación."),
    "scenes": [
        story(N, "nash",
              "Profe Nash: 'Macrosoft y tú son los jugadores. Cada uno puede elegir una estrategia: "
              "mantener el precio o bajarlo. Los pagos dependen de la combinación elegida.'",
              [ch("Entiendo: mi resultado depende también de lo que haga Bill", {"innovation": 2},
                  "En teoría de juegos, el pago de cada jugador depende de las decisiones de todos.",
                  "Interdependencia estratégica"),
               ch("Da igual lo que haga Bill, yo fijo mi precio", {"reputation": -2},
                  "Ignorar al otro jugador es un error: en un juego el pago depende de ambos.",
                  "Interdependencia estratégica")]),
        story(B, "bill",
              "Bill Gatez anuncia un clon barato del Aple II. 'Amigo, el mercado es chico. Bajaré mis "
              "precios si hace falta.' Tu equipo exige una respuesta inmediata.",
              [ch("Probar a cooperar: mantener el precio y observar", {"reputation": 2},
                  "Empezar cooperando es una señal positiva y reduce el riesgo de escalada.",
                  "Señalización"),
               ch("Contraatacar con un recorte inmediato", {"reputation": -2, "cash": -2000},
                  "Una reacción impulsiva puede arrastrar a ambos a una guerra de precios.",
                  "Escalada")]),
        {"type": "matrix",
         "text": "Ronda de precios contra Macrosoft. Si ambos mantienen, ganan bien; si uno baja solo, "
                 "se lleva el mercado. Si ambos bajan, los márgenes se destruyen.",
         "rival": "Macrosoft", "rounds": 3, "ai": "tit_for_tat",
         "options": ["Mantener precio", "Bajar precio"],
         "payoffs": [[[3, 3], [0, 5]], [[5, 0], [1, 1]]],
         "effects_per_point": {"cash": 1500, "reputation": 1},
         "explain": ("Dilema del prisionero: bajar el precio es la estrategia dominante para cada "
                     "jugador, así que (Bajar, Bajar) es el equilibrio de Nash con pagos (1,1). "
                     "Ambos estarían mejor en (Mantener, Mantener) con pagos (3,3), el óptimo "
                     "cooperativo. Como el juego se repite, el rival 'ojo por ojo' premia la "
                     "cooperación y castiga la traición.")},
        story(N, "nash",
              "Profe Nash: 'Notas el patrón: quien traiciona gana hoy, pero pierde la confianza para "
              "las próximas rondas. Mañana, Macrosoft y tú votan un estándar común de enchufes.'",
              [ch("Proponer un estándar abierto a Macrosoft", {"reputation": 2, "innovation": 2, "flag": "propuso_estandar"},
                  "Ofrecer cooperación creíble es la base de una alianza estratégica.",
                  "Cooperación"),
               ch("Guardar el estándar como ventaja propia", {"innovation": 2, "reputation": -3},
                  "Proteger tu tecnología te da ventaja, pero cierra puertas a alianzas.",
                  "Ventaja competitiva")]),
        {"type": "matrix",
         "text": "Alianza de estándares: pueden compartir sus conectores (Compartir) o cerrarlos "
                 "(Cerrar). Macrosoft usa una estrategia 'grim': si traicionas una vez, nunca perdona.",
         "rival": "Macrosoft", "rounds": 3, "ai": "grim",
         "options": ["Compartir estándar", "Cerrar estándar"],
         "payoffs": [[[4, 4], [0, 5]], [[5, 0], [1, 1]]],
         "effects_per_point": {"cash": 1200, "innovation": 1, "reputation": 1},
         "explain": ("La estrategia 'grim trigger' coopera hasta que el otro traiciona y luego "
                     "castiga para siempre. Es una amenaza creíble que sostiene la cooperación "
                     "si el jugador valora el futuro. Aun así, traicionar da 5 hoy y 1 después; "
                     "cooperar da 4 cada ronda. A largo plazo cooperar es el mejor curso.")},
        story("Lola Titular", "prensa",
              "Titular de Lola Titular: 'El duelo Aple–Macrosoft redefine el mercado'. Los clientes "
              "preguntan si seguirán las guerras de precios.",
              [ch("Reafirmar el compromiso con precios justos y alianzas", {"reputation": 2, "morale": 2},
                  "Una reputación de cooperador confiable es un activo en juegos repetidos.",
                  "Reputación"),
               ch("Declarar que Macrosoft es el enemigo", {"reputation": 2, "morale": 2, "rival.reputation": -3},
                  "Un enemigo común une al equipo, pero reduce opciones de cooperar luego.",
                  "Identidad de grupo")]),
    ],
})

# ===== 5. La junta directiva: poder y política =====
CHAPTERS.append({
    "id": "junta",
    "title": "Capítulo 5 · La junta directiva",
    "concept": "Poder y política: bases de French y Raven",
    "lesson": ("French y Raven identifican cinco bases de poder: legítimo (el cargo), de recompensa "
               "(premios), coercitivo (castigos), experto (conocimiento) y referente (carisma o "
               "admiración). El poder se ejerce también en la política organizacional mediante "
               "coaliciones y negociación. Un líder con una sola base de poder es vulnerable."),
    "scenes": [
        story(S, "scully",
              "John Scully, el CEO que contrataste, ahora te desafía. 'Tu visión es genial, pero la "
              "empresa pierde dinero. La junta me apoya.' El ambiente se vuelve tenso.",
              [ch("Recordarle que fundé la empresa y tengo el cargo", {"power.legitimo": 4, "reputation": -2},
                  "Apelar al cargo es poder legítimo: efectivo mientras los demás lo reconozcan.",
                  "Poder legítimo"),
               ch("Mostrar mis conocimientos técnicos del producto", {"power.experto": 6, "reputation": 2},
                  "El poder experto se basa en lo que sabes y aportas, difícil de quitar.",
                  "Poder experto"),
               ch("Amenazar con renunciar y llevarme al equipo", {"power.coercitivo": 6, "morale": -4},
                  "El poder coercitivo funciona por miedo, pero daña las relaciones.",
                  "Poder coercitivo"),
               ch("Hablar con el equipo sobre nuestra visión", {"power.referente": 6, "morale": 2},
                  "El poder referente nace de la admiración; ayuda a conseguir apoyo.",
                  "Poder referente")]),
        story("La Junta", "junta",
              "La junta convoca una votación. Hay tres directores indecisos. 'Cada uno quiere algo "
              "distinto: acciones, estabilidad, o un buen producto.'",
              [ch("Ofrecer acciones y bonos a los directores", {"cash": -6000, "power.recompensa": 8, "flag": "coalicion"},
                  "Aliarse con incentivos genera coaliciones, aunque cuesta recursos.",
                  "Poder de recompensa"),
               ch("Presentar datos del producto y el mercado", {"power.experto": 6, "reputation": 2, "flag": "coalicion"},
                  "La credibilidad técnica convence a los indecisos y crea una coalición sólida.",
                  "Poder experto"),
               ch("Presionar con filtraciones a la prensa", {"power.coercitivo": 8, "reputation": -8},
                  "La presión puede dar votos, pero compromete reputación y confianza.",
                  "Política sucia"),
               ch("Contar con mi cargo y no hacer campaña", {"power.legitimo": 3, "reputation": -2},
                  "Confiar solo en el puesto es arriesgado cuando no hay apoyo interno.",
                  "Política organizacional", {"min": {"power.legitimo": 5}}),
               ch("Pedir apoyo a empleados y clientes leales", {"power.referente": 8, "morale": 2, "reputation": 2, "flag": "coalicion"},
                  "La lealtad personal se vuelve respaldo político: tu influencia es de referente.",
                  "Poder referente", {"min": {"power.referente": 12}})]),
        story("La Junta", "junta",
              "Resultado: sin coalición y con poca influencia, la junta te quita el control. Te "
              "ofrecen un puesto simbólico. ¿Aceptas?",
              [ch("Aceptar y esperar mi momento", {"morale": -10, "reputation": -5, "flag": "expulsado", "progress": -8},
                  "Perder el cargo te deja sin poder legítimo; deberás reconstruir tu influencia.",
                  "Pérdida de poder"),
               ch("Rechazar y marcharme", {"morale": -14, "cash": -4000, "flag": "expulsado", "progress": -12},
                  "Salir sin plan te deja sin recursos; aún puedes regresar con apoyo.",
                  "Salida")],
              requires={"not_flag": "coalicion"}),
        story("Narrador", "nash",
              "El golpe llega: la junta vota 'reorganizar'. Pero tu coalición sostiene tu lugar. "
              "Scully intenta negociar un pacto de coexistencia.",
              [ch("Aceptar compartir decisiones con Scully", {"morale": 2, "reputation": 2, "power.legitimo": 3},
                  "Pactar con un rival transforma el conflicto en cooperación productiva.",
                  "Negociación"),
               ch("Echar a Scully ahora que tengo los votos", {"morale": -3, "progress": -3, "power.coercitivo": 6, "reputation": -3},
                  "Usar la fuerza consolida control inmediato, pero tiene costo político.",
                  "Poder coercitivo")],
              requires={"flag": "coalicion", "not_flag": "expulsado"}),
        story("Narrador", "nash",
              "Sin el cargo, tu círculo sigue creyendo en ti. Es 1996: Aple está en crisis. La junta "
              "te necesita... y tú necesitas una estrategia para volver.",
              [ch("Volver como asesor para aportar mi conocimiento", {"power.experto": 10, "reputation": 2, "progress": 2, "unflag": "expulsado", "flag": "regreso"},
                  "Regresar con poder experto legitima tu retorno ante la junta.",
                  "Poder experto", {"min": {"power.experto": 8}}),
               ch("Reunir al equipo leal y volver con su respaldo", {"power.referente": 10, "morale": 4, "progress": 2, "unflag": "expulsado", "flag": "regreso"},
                  "El respaldo del equipo muestra tu liderazgo referente.",
                  "Poder referente", {"min": {"power.referente": 8}}),
               ch("Comprar acciones y negociar mi regreso", {"cash": -8000, "power.legitimo": 8, "reputation": 2, "unflag": "expulsado", "flag": "regreso"},
                  "Recuperar poder legítimo a base de recursos funciona, pero es costoso.",
                  "Poder legítimo"),
               ch("Quedarme fuera lamentando mi suerte", {"morale": -6, "reputation": -4},
                  "La inacción te deja fuera del juego político.",
                  "Pasividad")],
              requires={"flag": "expulsado"}),
        story(S, "scully",
              "Cierre del conflicto. Scully deja la empresa o se queda. La junta te reconoce como "
              "líder del próximo ciclo si cuidas a los equipos y a los accionistas.",
              [ch("Reorganizar la empresa con un equipo diverso", {"morale": 2, "reputation": 2, "progress": 2},
                  "Integrar bases de poder diversas fortalece la gobernanza.",
                  "Gobernanza"),
               ch("Concentrar todas las decisiones en mí", {"progress": 2, "morale": -6, "power.legitimo": 5},
                  "Concentrar poder acelera decisiones, pero aumenta el riesgo de otro golpe.",
                  "Concentración de poder")]),
    ],
})

# ===== 6. El gran trato =====
CHAPTERS.append({
    "id": "trato",
    "title": "Capítulo 6 · El gran trato",
    "concept": "Negociación e innovación cooperativa",
    "lesson": ("En negociación integrativa se busca expandir el valor ('agrandar el pastel') en vez de "
               "dividirlo; se parte de intereses y no de posiciones. Un juego de coordinación tiene "
               "varios equilibrios de Nash, y la comunicación y la confianza ayudan a elegir el "
               "mejor. La reputación acumulada determina qué alianzas son posibles."),
    "scenes": [
        story(E, "mosk",
              "Elon Mosk te cita en su fábrica de cohetes. 'Tu hardware con mi software de cohetes y "
              "autos... podríamos llegar a Marte. Pero no firmo con cualquiera.'",
              [ch("Preguntar por sus intereses reales", {"reputation": 2, "innovation": 2},
                  "Negociar por intereses y no por posiciones abre soluciones creativas.",
                  "Negociación por intereses"),
               ch("Empezar hablando del precio", {"reputation": -2},
                  "Centrarse en el precio reduce el valor total posible de la negociación.",
                  "Negociación posicional")]),
        story(E, "mosk",
              "Mosk pide ver tu historial: '¿Cumples lo que prometes? Dime qué me ofreces'.",
              [ch("Mostrar nuestro prototipo más innovador", {"innovation": 2, "reputation": 2, "flag": "demo_mosk"},
                  "Una demostración concreta respalda tu propuesta de valor.",
                  "Propuesta de valor", {"min": {"innovation": 45}}),
               ch("Mostrar resultados financieros sólidos", {"reputation": 2, "cash": 4000, "flag": "demo_mosk"},
                  "La solidez financiera da credibilidad a la alianza.",
                  "Credibilidad", {"min": {"cash": 15000}}),
               ch("Confiar en mi carisma", {"reputation": 2, "morale": 2},
                  "El carisma ayuda, pero necesita respaldo en hechos.",
                  "Persuasión")]),
        {"type": "matrix",
         "text": "Negociación con Mosk: elijan entre una alianza abierta (Colaborar) o proteger su "
                 "tecnología (Proteger). Coordinarse en Colaborar rinde más a largo plazo. Mosk es "
                 "impredecible.",
         "rival": "Elon Mosk", "rounds": 3, "ai": "random",
         "options": ["Colaborar", "Proteger tecnología"],
         "payoffs": [[[5, 5], [1, 3]], [[3, 1], [2, 2]]],
         "effects_per_point": {"cash": 1800, "innovation": 1, "reputation": 1},
         "explain": ("Este juego de coordinación tiene dos equilibrios de Nash: (Colaborar, Colaborar) "
                     "con pagos (5,5) y (Proteger, Proteger) con pagos (2,2). El primero es mejor "
                     "para ambos. Comunicarse y generar confianza ayuda a coordinarse en el mejor "
                     "equilibrio.")},
        story(E, "mosk",
              "Mosk: 'Última pregunta. ¿Qué hago con tu empresa si firmamos? ¿Qué le pasa al equipo?'",
              [ch("Una alianza donde todos ganan: tecnología compartida y participación", {"reputation": 2, "morale": 2, "innovation": 2, "flag": "oferta_cooperativa"},
                  "Una propuesta integrativa expande el valor para ambas partes.",
                  "Negociación integrativa"),
               ch("Exigir control total del acuerdo", {"cash": 5000, "reputation": -6, "morale": -4},
                  "La negociación distributiva gana más hoy, pero deteriora la relación.",
                  "Negociación distributiva"),
               ch("Retrasar la decisión para ver qué hace Macrosoft", {"reputation": -2, "innovation": 2},
                  "Esperar demasiado puede hacer perder una ventana de oportunidad.",
                  "Oportunidad")]),
        story(E, "mosk",
              "Mosk extiende la mano. 'Si de verdad innovas, cooperas y tu empresa es sólida, firmo. "
              "De lo contrario, buena suerte con Macrosoft.'",
              [ch("Firmar la alianza: ¡rumbo a Marte!", {"reputation": 4, "innovation": 4, "morale": 2, "flag": "trato_mosk"},
                  "Tu historial de innovación y cooperación hace posible el gran trato.",
                  "Alianza estratégica",
                  {"min": {"reputation": 55, "innovation": 50}, "flag": "oferta_cooperativa"}),
               ch("Firmar un acuerdo modesto de proveedor", {"cash": 6000, "reputation": 2},
                  "Un acuerdo menor asegura ingresos, pero sin visión compartida.",
                  "Acuerdo limitado"),
               ch("Rechazar y seguir independiente", {"morale": 2, "innovation": 2},
                  "Mantener independencia evita riesgos, pero renuncia a sinergias.",
                  "Independencia")]),
    ],
})
