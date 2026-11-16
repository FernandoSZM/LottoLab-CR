
WITH sorteos_diarios AS (
    SELECT
        draw_date,
        COUNT(*) AS cantidad
    FROM draws
    GROUP BY draw_date
)
SELECT
    MIN(draw_date) FILTER (
        WHERE cantidad = 3
    ) AS primer_dia_con_tres_sorteos,

    MAX(draw_date) FILTER (
        WHERE cantidad = 2
          AND draw_date >= DATE '2022-01-01'
          AND draw_date < DATE '2023-01-01'
    ) AS ultimo_dia_con_dos_en_2022
FROM sorteos_diarios;
