# PySpark Performance Optimization

## 1. Stay in JVM

Prefer built-in SQL/functions to avoid the Python/JVM serialization overhead:

**Avoid Python UDFs:**
```python
# Slow - Python UDF
from pyspark.sql.functions import udf

@udf('string')
def slow_upper(s):
    return s.upper()

df.withColumn('name_upper', slow_upper('name'))  # ❌ Serialization overhead
```

**Use built-in functions:**
```python
# Fast - JVM built-in
from pyspark.sql.functions import upper

df.withColumn('name_upper', upper('name'))  # ✅ Stays in JVM
```

**If custom logic is unavoidable, use Pandas UDFs (vectorized):**
```python
from pyspark.sql.functions import pandas_udf
import pandas as pd

@pandas_udf('double')
def vectorized_calculation(s: pd.Series) -> pd.Series:
    return s * 2.5 + 10  # Operates on entire column at once

df.withColumn('result', vectorized_calculation('value'))  # ✅ Vectorized
```

## 2. Smart Joins

### Broadcast Small Tables

Use `broadcast()` to avoid shuffling when joining with small dimension tables:

```python
from pyspark.sql.functions import broadcast

# Broadcast the small side to eliminate shuffle
result = big_df.join(broadcast(dim_df), 'id')
```

**When to broadcast:**
- Table fits in driver and executor memory (< 100MB typically)
- Joining large fact table with small dimension table
- Avoiding expensive shuffle operations

**Broadcast join hints:**
```python
# SQL hint syntax
spark.sql("""
    SELECT /*+ BROADCAST(dim) */ *
    FROM events e
    JOIN dim ON e.dim_id = dim.id
""")
```

### Configure Broadcast Threshold

```python
# Auto-broadcast tables smaller than 64MB
spark.conf.set('spark.sql.autoBroadcastJoinThreshold', '64MB')
```

## 3. Partition Intelligently

### Shuffle Partitions

Set `spark.sql.shuffle.partitions` based on cluster size:

```python
# Rule of thumb: #executors × 2-3
# For 16 executors with 4 cores each = 128 partitions
spark.conf.set('spark.sql.shuffle.partitions', 128)
```

### Repartition vs Coalesce

**Use `repartition(col)` early for skewed keys:**
```python
# Distribute data evenly by key before expensive operations
df = df.repartition('user_id')
```

**Use `coalesce(n)` before narrow sinks:**
```python
# Reduce number of output files without full shuffle
df.coalesce(10).write.parquet('output/')
```

## 4. Cache/Persist Selectively

**When to Persist:**

Persist only when a DataFrame/RDD will be reused by more than one *action* or across different branches of the DAG. Otherwise Spark will recompute each time.

**Heuristics:**
- Persist after expensive, pure transformations
- Put `.persist(...)` immediately after the transformation you do *not* want repeated
- Trigger a cheap action like `.count()` to materialize the cache

### Storage Levels

Pick the right storage level for your use case:

| Scenario                                         | StorageLevel          |
| ------------------------------------------------ | --------------------- |
| Fits comfortably in executor memory              | `MEMORY_ONLY`         |
| Slightly too large for memory                    | `MEMORY_AND_DISK`     |
| Very large or many columns; prefer serialization | `MEMORY_AND_DISK_SER` |

**Example:**
```python
from pyspark.storagelevel import StorageLevel

featured_df = (raw_df
               .filter("event_type = 'click'")
               .withColumn('date', to_date('ts'))
               .persist(StorageLevel.MEMORY_AND_DISK))

featured_df.count()  # Materialize once

# Reuse in multiple operations
clicks_by_day = featured_df.groupBy('date').count()
clicks_by_user = featured_df.groupBy('user_id').count()

# Clean up when done
featured_df.unpersist(blocking=True)
```

### Caching Best Practices

**Don't cache:**
- Tiny dimension tables you intend to broadcast (broadcast already keeps them in memory)
- DataFrames used only once
- Very large DataFrames that won't fit in memory

**Do cache:**
- DataFrames reused in multiple actions
- Iterative algorithms (ML training loops)
- Interactive analysis workflows

**Monitor caching:**
- Watch Spark UI → *Storage* tab
- Look for un-/deserialized size and eviction events
- If cached DataFrame shows 0% cached, partitions were evicted or never materialized

**Unpersist aggressively:**
```python
df.unpersist(blocking=True)  # Free memory when done
```

**Skew & partitions:**
- Repartition *before* persisting
- Caching a skewed DataFrame wastes memory and leaves hot partitions

**AQE interactions:**
- Persisting after wide transformations can prevent Spark from re-planning upstream stages (good)
- But may hinder dynamic coalescing (bad)
- Benchmark to find the right balance

## 5. File Formats & I/O

### Use Columnar Formats

Store in **Parquet** format with compression:

```python
# Write with compression
df.write \
  .mode('overwrite') \
  .option('compression', 'zstd') \
  .parquet('output/')
```

**Why Parquet:**
- Columnar storage enables column pruning
- Excellent compression ratios
- Supports predicate pushdown
- Industry standard for analytics

**Compression options:**
- `snappy` - Fast compression/decompression (default)
- `zstd` - Better compression ratio, slightly slower
- `gzip` - Best compression, slowest

### Push Filters Down

Filter and select early to minimize data movement:

```python
# Good - filter before expensive operations
df = spark.read.parquet('events/') \
    .filter("event_date >= '2025-01-01'") \
    .select('user_id', 'ts', 'event_type')

# Bad - filter after reading all columns
df = spark.read.parquet('events/') \
    .select('user_id', 'ts', 'event_type', 'extra1', 'extra2', 'extra3') \
    .filter("event_date >= '2025-01-01'")
```

## 6. Monitor & Tune

### Spark UI

Use the Spark UI (`:4040`) to identify bottlenecks:

- **Jobs tab** - See job durations and failures
- **Stages tab** - Identify slow stages, skewed tasks
- **Storage tab** - Monitor cached DataFrames
- **Executors tab** - Check CPU utilization, memory usage
- **SQL tab** - View query plans and execution details

### Explain Plans

Use `.explain()` to understand query execution:

```python
df.explain('formatted')  # Pretty-printed physical plan
```

### Enable Adaptive Query Execution (AQE)

```python
spark.conf.set('spark.sql.adaptive.enabled', 'true')
spark.conf.set('spark.sql.adaptive.skewJoin.enabled', 'true')
```

**Benefits:**
- Dynamically coalesce shuffle partitions
- Handle skewed joins automatically
- Convert sort-merge joins to broadcast joins when possible

## 7. Configuration Quick-Hits

```python
# Auto-broadcast threshold
spark.conf.set('spark.sql.autoBroadcastJoinThreshold', '64MB')

# Reuse Python workers
spark.conf.set('spark.python.worker.reuse', 'true')

# Enable AQE
spark.conf.set('spark.sql.adaptive.enabled', 'true')

# Skew join handling
spark.conf.set('spark.sql.adaptive.skewJoin.enabled', 'true')
```

## 8. Example High-Performance Pattern

Putting it all together:

```python
from pyspark.sql import DataFrame
from pyspark.sql.functions import broadcast

def enrich_events(events: DataFrame, users: DataFrame) -> DataFrame:
    """
    High-performance event enrichment with user data.

    Optimizations:
    - Filter early to minimize data movement
    - Select only needed columns
    - Broadcast small dimension table
    - Repartition by output partition key
    - Use efficient compression
    """
    # Minimal columns, predicate push-down
    events = events.filter("event_date >= '2025-01-01'") \
                   .select('user_id', 'ts', 'event_type')

    # Broadcast small dimension
    users_small = users.select('user_id', 'country') \
                       .filter("country = 'US'")
    joined = events.join(broadcast(users_small), 'user_id')

    # Write once, coalesce to large files
    return (joined
            .repartition('country')
            .write
            .mode('overwrite')
            .option('compression', 'zstd')
            .partitionBy('country')
            .parquet('output/'))
```

## Performance Checklist

- ✅ Use built-in functions over Python UDFs
- ✅ Broadcast small joins (< 100MB)
- ✅ Set `spark.sql.shuffle.partitions` based on cluster size
- ✅ Persist only when reused ≥ 2 actions
- ✅ Unpersist aggressively when done
- ✅ Store in Parquet with compression (Snappy/ZSTD)
- ✅ Filter and select early (predicate pushdown)
- ✅ Monitor Spark UI after each change
- ✅ Enable AQE and skew join handling
- ✅ Never `collect()` large datasets - use `.limit()` for inspection
