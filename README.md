# cdl-compiler

## Integrantes
- Alfredo Montero López
- Leonardo Amaro Rodriguez
- Anthuan Montes de Oca Pons

## Descripción
### Lexer:
- Implementación del regex estándar (no extendido). Incluye la implementación de rangos([a..z])
- Utilización de un LR1Parser para construir la gramática del regex.
- Creación de un autómata que reconoce todas las expresiones permitidas por el regex.
- Iteración sobre el código para obtener los tokens.
### Parser:
- Utilización del mismo LR1Parser para construir la gramática de HULK.
- Implementación del HULK básico.
- Obtención del AST correspondiente al código a ejecutar.
### Chequeo Semántico:
- Realizado mediante el recorrido del AST con 3 visitantes diferentes:
    - Descubrimiento de los tipos existentes en el código.
    - Construcción de los tipos (relaciones de herencia, métodos y atributos).
    - Comprobación de la concordancia de tipos, parámetros, declaraciones de variables, etc.
### Intérprete:
- Se utiliza un visitante para encontrar los nodos de cada función.
- Cada nodo del AST tiene una función evaluate que devuelve el valor de evaluar la expresión correspondiente.