select
  id,
  loaded_at
from {{ ref('stg_example') }}

