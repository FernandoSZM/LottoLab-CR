
-- LottoLab CR
-- Auditoria de horarios duplicados
-- Detecta sorteos que comparten fecha y hora

SELECT
    draw_date AS fecha,
    draw_time AS hora,
    COUNT(*) AS cantidad,
    STRING_AGG(
        draw_id::TEXT,
        ', '
        ORDER BY draw_id
    ) AS sorteos
FROM draws
GROUP BY draw_date, draw_time
HAVING COUNT(*) > 1
ORDER BY draw_date, draw_time;
