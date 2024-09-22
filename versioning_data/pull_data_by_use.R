
pull_data_by_usi_query <- function(target_usi) {
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
-- find any relevant row deletions
-- with _usi no larger than target_usi
deletion_scan AS (
   SELECT
     _fi,
     MAX(_usi) AS _usi
   FROM 
     d_row_deletions
   WHERE
     _usi <= {target_usi}
   GROUP BY
     _fi
),
-- collect state of each row
-- including possibly relevant deletions
chosen_marks AS (
  SELECT
    data_scan._fi AS _fi,
    data_scan._usi AS _usi,
    deletion_scan._fi AS _deleted_fi,
    deletion_scan._usi AS _deleted_usi
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
   chosen_marks
ON
  d_data_log._fi = chosen_marks._fi
  AND d_data_log._usi = chosen_marks._usi
WHERE
   (chosen_marks._deleted_fi is NULL)
   OR (chosen_marks._deleted_usi < chosen_marks._usi)
ORDER BY
   d_data_log._fi,
   d_data_log._usi
", fixed = TRUE))
}

pull_data_by_usi <- function(con, target_usi, return_intenal_keys = FALSE) {
  q <- pull_data_by_usi_query(target_usi)
  res <- dbGetQuery(con, q)
  if (!return_intenal_keys) {
    res["_fi"] <- NULL
    res["_usi"] <- NULL
  }
  return(res)
}
