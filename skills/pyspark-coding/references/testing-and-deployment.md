# PySpark Testing and Deployment

## Testing Strategy

### Test with Real Spark - Not Mocks

Don't mock Spark - test with a real local Spark context:

```python
# conftest.py
import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope='session')
def spark():
    """Shared Spark session for all tests."""
    return (SparkSession.builder
            .master('local[2]')
            .appName('test')
            .getOrCreate())
```

**Why test with real Spark:**
- Catches actual PySpark API issues
- Tests schema evolution and type handling
- Validates Catalyst optimization behavior
- Fast enough with `local[2]` for unit tests

### Equality Helpers

Use `chispa` or `pyspark.testing.utils` for DataFrame equality:

**With chispa (recommended):**
```python
from chispa import assert_df_equality

def test_remove_spaces(spark):
    # Arrange
    src = spark.createDataFrame([('John    D.',)], ['name'])
    expected = spark.createDataFrame([('John D.',)], ['name'])

    # Act
    actual = remove_extra_spaces(src)

    # Assert
    assert_df_equality(actual, expected)
```

**With built-in utils:**
```python
from pyspark.testing.utils import assertDataFrameEqual

def test_filter_clicks(spark):
    input_df = spark.createDataFrame([
        ('click', 100),
        ('view', 200),
        ('click', 150)
    ], ['event_type', 'count'])

    expected = spark.createDataFrame([
        ('click', 100),
        ('click', 150)
    ], ['event_type', 'count'])

    actual = filter_events(input_df, 'click')
    assertDataFrameEqual(actual, expected)
```

**Benefits:**
- Declarative assertions
- Good diff output when tests fail
- Handles schema comparison
- Column order insensitive

### Structure Code for Tests

Organize code to separate I/O from transformations:

```
mypackage/
 ├─ jobs/
 │   └─ main.py        # SparkSession creation, orchestration
 ├─ etl/
 │   ├─ transforms.py  # Pure functions -> unit test here
 │   └─ io.py          # Read/write helpers
 └─ tests/
     ├─ conftest.py
     └─ test_transforms.py
```

**Pure transformation example:**
```python
# etl/transforms.py
from pyspark.sql import DataFrame
from pyspark.sql.functions import regexp_replace

def remove_extra_spaces(df: DataFrame) -> DataFrame:
    """Remove extra spaces from name column."""
    return df.withColumn('name', regexp_replace('name', r'\s+', ' '))
```

**Test example:**
```python
# tests/test_transforms.py
from mypackage.etl.transforms import remove_extra_spaces
from chispa import assert_df_equality

def test_remove_extra_spaces(spark):
    input_df = spark.createDataFrame([
        ('John    D.',),
        ('Jane  Doe',)
    ], ['name'])

    expected = spark.createDataFrame([
        ('John D.',),
        ('Jane Doe',)
    ], ['name'])

    actual = remove_extra_spaces(input_df)
    assert_df_equality(actual, expected)
```

**Benefits:**
- Tests run in <1 second with `local[2]`
- No external dependencies (S3, databases)
- Easy to reason about inputs and outputs
- Reproducible test data

### Testing Best Practices

**DO:**
- ✅ Test transformations with small, focused DataFrames
- ✅ Use `spark.createDataFrame()` for test data
- ✅ Test edge cases (null values, empty DataFrames, duplicates)
- ✅ Use `chispa` or `assertDataFrameEqual` for assertions
- ✅ Keep tests fast (<1s per test)

**DON'T:**
- ❌ Mock Spark objects
- ❌ Test with production data in unit tests
- ❌ Use `collect()` then compare Python lists (loses schema info)
- ❌ Mix I/O with transformation logic
- ❌ Skip edge case testing

## Parallelism & Deployment

### Local Development (Laptop)

Configuration for local development and testing:

```python
spark = (SparkSession.builder
         .master('local[*]')  # Use all logical CPU cores
         .config('spark.sql.shuffle.partitions', 4)  # Avoid 200 tiny tasks
         .config('spark.default.parallelism', 8)  # 4-core laptop example
         .getOrCreate())
```

**Local development settings:**

| Parameter                      | Recommended Value | Notes                          |
| ------------------------------ | ----------------- | ------------------------------ |
| `master`                       | `local[*]`        | Use all logical cores          |
| `spark.sql.shuffle.partitions` | 4-8               | Avoid hundreds of tiny tasks   |
| `spark.default.parallelism`    | 2 × (# cores)     | For RDD-heavy operations       |

**Why these settings:**
- `local[*]` maximizes local CPU usage
- Small shuffle partitions prevent task overhead on small datasets
- Reasonable parallelism for laptop-scale data

### Cluster / Production Deployment

Configuration for YARN/Kubernetes cluster deployment:

**Sizing rules of thumb:**

| Parameter                      | Rule of Thumb                 | Example (8 nodes × 4 cores) |
| ------------------------------ | ----------------------------- | --------------------------- |
| `--executor-cores`             | 3-5                           | 4                           |
| `--num-executors`              | total_cores / executor.cores  | 16                          |
| `spark.default.parallelism`    | executors × cores × 2         | 128                         |
| `spark.sql.shuffle.partitions` | match default.parallelism     | 128                         |

**Example spark-submit:**
```bash
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --num-executors 16 \
  --executor-cores 4 \
  --executor-memory 8G \
  --driver-memory 4G \
  --conf spark.default.parallelism=128 \
  --conf spark.sql.shuffle.partitions=128 \
  --conf spark.sql.adaptive.enabled=true \
  --conf spark.sql.adaptive.skewJoin.enabled=true \
  --conf spark.python.worker.reuse=true \
  my_job.py
```

**Production best practices:**
- Enable Adaptive Query Execution (AQE)
- Set shuffle partitions to match cluster parallelism
- Reuse Python workers to avoid startup overhead
- Monitor Spark UI (Stages & Executors tabs) for tuning
- Start conservative, scale up based on metrics

### Environment-Specific Configuration

Use different configurations per environment:

```python
# config.py
def get_spark_config(env: str):
    """Get environment-specific Spark configuration."""
    if env == 'local':
        return {
            'spark.master': 'local[*]',
            'spark.sql.shuffle.partitions': '4',
            'spark.default.parallelism': '8'
        }
    elif env == 'production':
        return {
            'spark.master': 'yarn',
            'spark.sql.shuffle.partitions': '128',
            'spark.default.parallelism': '128',
            'spark.sql.adaptive.enabled': 'true'
        }
    else:
        raise ValueError(f"Unknown environment: {env}")

# main.py
import os
from config import get_spark_config

env = os.getenv('ENV', 'local')
config = get_spark_config(env)

spark = SparkSession.builder.appName('my-job')
for key, value in config.items():
    spark = spark.config(key, value)
spark = spark.getOrCreate()
```

### Deployment Checklist

Before deploying to production:

- ✅ Test with representative data volume locally
- ✅ Profile with Spark UI to identify bottlenecks
- ✅ Set appropriate executor cores and memory
- ✅ Configure shuffle partitions based on cluster size
- ✅ Enable AQE and skew join handling
- ✅ Set up monitoring and alerting
- ✅ Document expected runtime and resource usage
- ✅ Have rollback plan ready

## Monitoring & Debugging

### Spark UI

Monitor these tabs after deployment:

**Jobs tab:**
- Job durations and success rates
- Failed jobs and error messages

**Stages tab:**
- Stage-level timings
- Task distribution and skew
- GC time (should be < 10% of task time)

**Storage tab:**
- Cached DataFrames and memory usage
- Eviction events

**Executors tab:**
- CPU utilization (should be high)
- Memory usage and GC patterns
- Failed tasks per executor

**SQL tab:**
- Query plans and execution details
- Identify expensive operations

### Common Issues & Solutions

**Issue: Long GC pauses**
- Solution: Reduce executor memory or increase number of executors
- Check: Executors tab → GC time

**Issue: Skewed partitions**
- Solution: Repartition by different key or use salting
- Check: Stages tab → task durations

**Issue: OOM errors**
- Solution: Increase executor memory or reduce parallelism
- Check: Executors tab → memory usage

**Issue: Slow shuffles**
- Solution: Broadcast small tables, reduce shuffle partitions
- Check: SQL tab → exchange operations

## Quick Reference Checklist

**Testing:**
- ✅ Test with real Spark context (`local[2]`)
- ✅ Use `chispa` or `assertDataFrameEqual`
- ✅ Keep transforms pure (no I/O)
- ✅ Cover edge cases (nulls, empty DataFrames)
- ✅ Keep tests fast (<1s)

**Local Development:**
- ✅ `master = local[*]`
- ✅ `shuffle.partitions = 4-8`
- ✅ `default.parallelism = 2 × cores`

**Production:**
- ✅ Size executors (3-5 cores, 8-16GB memory)
- ✅ `shuffle.partitions = executors × cores × 2`
- ✅ Enable AQE and skew handling
- ✅ Monitor Spark UI continuously
- ✅ Document expected performance
