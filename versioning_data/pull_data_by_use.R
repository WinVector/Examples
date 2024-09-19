
pull_data_by_usi <- function(target_usi) {
  return (gsub("{target_usi}", target_usi, "
-- Pull what was known at sequence
-- target_usi = {target_usi}
WITH 
-- find data rows with freshest
-- update sequence index per fact id
-- with _usi no larger than target_usi
data_scan AS (  
   SELECT
     _fi,
     MAX(_usi) AS _usi
   FROM 
     d_data_log
   WHERE
     _usi <= {target_usi}
   GROUP BY
     _fi
),
-- find any row deletions
-- with _usi no larger than target_usi
deletion_scan AS (
   SELECT
     _fi
   FROM 
     d_row_deletions
   WHERE
     _usi <= {target_usi}
   GROUP BY
     _fi
),
-- simulate an anti-join to mark 
-- which rows not considered deleted
chosen_fi AS (  
  SELECT
    data_scan.*,
    deletion_scan._fi AS _deleted_fi
  FROM
    data_scan
  LEFT JOIN
    deletion_scan
  ON
    data_scan._fi = deletion_scan._fi
)
-- Use chosen ids to pull correct rows
-- target_usi = {target_usi}
SELECT  
   d_data_log.*
FROM
   d_data_log
INNER JOIN
   chosen_fi
ON
  d_data_log._fi = chosen_fi._fi
  AND d_data_log._usi = chosen_fi._usi
WHERE
   chosen_fi._deleted_fi is NULL
ORDER BY
   d_data_log._fi,
   d_data_log._usi
", fixed = TRUE))
}