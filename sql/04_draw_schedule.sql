
-- LottoLab CR
-- Horarios registrados alrededor del cambio de 2022

SELECT
    draw_date AS fecha,
    COUNT(*) AS cantidad_sorteos,
    STRING_AGG(
        TO_CHAR(draw_time, 'HH24:MI'),
        ', '
        ORDER BY draw_time
    ) AS horarios
FROM draws
WHERE draw_date BETWEEN
    DATE '2022-03-28'
    AND DATE '2022-04-11'
GROUP BY draw_date
ORDER BY draw_date;
