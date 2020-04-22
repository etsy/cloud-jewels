WITH jewel_coefficients AS (
  SELECT 'CPU' AS jewel_class, 1/(60*60) AS scaling_constant, 2.11 AS jewel_coefficient
  UNION ALL
  SELECT 'GPU' AS jewel_class, 1/(60*60) AS scaling_constant, 2.11 AS jewel_coefficient
  UNION ALL
  SELECT 'Cloud Storage' AS jewel_class, 1.0/power(1000,4)/(60.0*60.0) AS scaling_constant, 0.89 AS jewel_coefficient
  UNION ALL
  SELECT 'Storage' AS jewel_class, 1.0/power(1000,4)/(60.0*60.0) AS scaling_constant, 0.89 AS jewel_coefficient
  UNION ALL
  SELECT 'SSD Storage' AS jewel_class, 1.0/power(1000,4)/(60.0*60.0) AS scaling_constant, 1.52 AS jewel_coefficient
), base AS (
  SELECT
    invoice.month,
    service.description as service_description,
    sku.description,
    sku.id,
    usage.unit,
    CASE
        WHEN service.description = 'Cloud Storage' and usage.unit = 'byte-seconds' THEN 'Cloud Storage' WHEN service.description = 'Support' THEN 'Excluded Service'
        WHEN service.description != 'Compute Engine' THEN 'Excluded Service'
        WHEN REGEXP_CONTAINS(sku.description, r'(?i)Commitment|Licensing Fee|External IP Charge|Vpn Tunnel|Global Forwarding Rule|Static Ip') THEN 'Excluded Service'
        WHEN REGEXP_CONTAINS(sku.description, r'(?i)\bcore|cpu\b') and usage.unit = 'seconds' THEN 'CPU'
        WHEN REGEXP_CONTAINS(sku.description, r'(?i)\bgpu\b') and usage.unit = 'seconds' THEN 'GPU'
        WHEN REGEXP_CONTAINS(sku.description, r'(?i)\bram\b') and usage.unit = 'byte-seconds' THEN 'Memory'
        WHEN REGEXP_CONTAINS(sku.description, r'(?i)\bstorage\b') and usage.unit = 'byte-seconds' THEN 'Storage'
        WHEN REGEXP_CONTAINS(sku.description, r'\bSSD backed PD Capacity$') and usage.unit = 'byte-seconds' THEN 'SSD Storage'
        WHEN REGEXP_CONTAINS(sku.description, r'(?i)network|traffic|interconnect') and usage.unit = 'bytes' THEN 'Network'
        ELSE 'Excluded Service'
    END AS jewel_class,
    SUM(cost)
      + SUM(IFNULL((SELECT SUM(c.amount)
                    FROM UNNEST(credits) c), 0))
      AS total_cost,
    (SUM(CAST(cost * 1000000 AS int64))
       + SUM(IFNULL((SELECT SUM(CAST(c.amount * 1000000 as int64))
                    FROM UNNEST(credits) c), 0))) / 1000000
      AS total_cost_exact,
    SUM(usage.amount) AS total_usage_amount
  FROM
    -- point to your GCP Billing Export table here
    <YOUR_BILLING_EXPORT_TABLE_HERE>
  WHERE
    DATE(_PARTITIONTIME) >= (DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY))
    AND usage_start_time >= TIMESTAMP(DATE_SUB(CURRENT_DATE, INTERVAL 29 DAY))
    -- remove zero-cost administrative SKUS (like 'Reserved Cores')
    AND cost > 0
  GROUP BY
    1,2,3,4,5,6
)
SELECT
  a.jewel_class,
  count(*) AS skus,
  coalesce(sum(
    a.total_usage_amount*scaling_constant*jewel_coefficient/1000
  ),0) AS cloud_jewels
FROM
  base AS a
LEFT JOIN
  jewel_coefficients as b ON b.jewel_class = a.jewel_class
GROUP BY
    1
ORDER BY
  cloud_jewels
DESC
;
