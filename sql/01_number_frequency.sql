
-- LottoLab CR
-- Analisis de frecuencia de numeros ganadores
-- Fuente: Nuevos Tiempos 2019-2025

WITH numeros AS (
    SELECT LPAD(n::TEXT, 2, '0') AS numero
    FROM generate_series(0, 99) AS n
),
frecuencias AS (
    SELECT
        winning_number AS numero,
        COUNT(*) AS apariciones
    FROM draws
    GROUP BY winning_number
)
SELECT
    n.numero,
    COALESCE(f.apariciones, 0) AS apariciones,
    ROUND(
        COALESCE(f.apariciones, 0) * 100.0 /
        (SELECT COUNT(*) FROM draws),
        2
    ) AS porcentaje,
    ROUND(
        (SELECT COUNT(*) FROM draws) / 100.0,
        2
    ) AS frecuencia_esperada
FROM numeros n
LEFT JOIN frecuencias f
    ON n.numero = f.numero
ORDER BY apariciones DESC, n.numero;
