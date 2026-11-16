
-- LottoLab CR
-- Cantidad de sorteos por dia y por anio

WITH sorteos_diarios AS (
    SELECT
        draw_date,
        EXTRACT(YEAR FROM draw_date)::INTEGER AS anio,
        COUNT(*) AS sorteos_dia
    FROM draws
    GROUP BY draw_date
)
SELECT
    anio,
    COUNT(*) AS dias_con_sorteos,
    SUM(sorteos_dia) AS total_sorteos,
    ROUND(AVG(sorteos_dia), 2) AS promedio_diario,
    MIN(sorteos_dia) AS minimo_diario,
    MAX(sorteos_dia) AS maximo_diario
FROM sorteos_diarios
GROUP BY anio
ORDER BY anio;
