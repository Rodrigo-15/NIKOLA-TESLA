-- crear una consulta postgresql que vea los dni duplicados de la tabal core_persona
-- y que me muestre el nombre de la persona y el dni duplicado
SELECT nombre, dni
FROM core_persona
WHERE numero_documento IN (
    SELECT numero_documento
    FROM core_persona
    GROUP BY numero_documento
    HAVING COUNT(numero_documento) > 1
)