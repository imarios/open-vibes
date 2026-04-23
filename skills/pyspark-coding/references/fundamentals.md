# PySpark Fundamentals

## Fundamental Principles

**DataFrame-first**: Default to the high-level `DataFrame`/Spark SQL API for its Catalyst optimization and Tungsten execution; drop down to RDDs only when you genuinely need low-level control.

**Pure transformations, late binding**: Separate I/O (read/write) from pure transformation functions that accept and return `DataFrame`s or `RDD`s; this keeps business logic testable.

**Single entry-point**: Create the `SparkSession` once in a small `main.py` (or `__main__.py`) and pass it downward; never call `SparkSession.builder` inside libraries.

## When to Use RDDs vs DataFrames

| Use DataFrame/Spark SQL when...                                  | Use RDD when...                                                                                |
| ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Data is structured/semi-structured (schema)                      | Data is *truly* unstructured or needs custom binary parsing                                    |
| Built-in or SQL functions express the operation                  | You need transformations unsupported in DataFrame (e.g. per-record stateful graph algorithms)  |
| You want the Catalyst optimizer, code-gen & Tungsten             | You need byte-level control, custom partitioning, or iterative ML algorithm not yet in MLlib   |
| You value automatic logical plan optimizations & column pruning  | You're ready to trade performance for flexibility                                              |

**Rule of thumb**: Start with DataFrames; fall back to RDDs **only** if a clear blocker appears. Conversions are cheap: `df.rdd` ⇄ `spark.createDataFrame(rdd, schema)`.

## Code Structure for Testability

Organize your PySpark code to separate concerns and enable fast unit testing:

```
mypackage/
 ├─ jobs/main.py        # build SparkSession, parse args, orchestrate
 ├─ etl/
 │   ├─ transforms.py   # pure functions -> unit test here
 │   └─ io.py           # read/write helpers
 └─ tests/
     └─ test_transforms.py
```

**Benefits:**
- Pure transformation functions can be unit tested with `local[2]` in <1 second
- I/O logic is isolated and can be mocked/stubbed as needed
- Business logic is independent of data sources
- Easy to reason about data flow

## SparkSession Management

**Single entry-point pattern:**

```python
# main.py
from pyspark.sql import SparkSession
from mypackage.etl import transforms

def main():
    spark = (SparkSession.builder
             .appName('my-job')
             .getOrCreate())

    # Read data
    events = spark.read.parquet('s3://bucket/events/')
    users = spark.read.parquet('s3://bucket/users/')

    # Call pure transformations (pass spark if needed for UDFs)
    result = transforms.enrich_events(events, users)

    # Write result
    result.write.mode('overwrite').parquet('s3://bucket/output/')

    spark.stop()

if __name__ == '__main__':
    main()
```

**Never do this in library code:**
```python
# transforms.py - DON'T DO THIS
def bad_transform(data):
    spark = SparkSession.builder.getOrCreate()  # ❌ Creates new session
    return spark.sql(f"SELECT * FROM {data}")
```

**Do this instead:**
```python
# transforms.py - GOOD
from pyspark.sql import DataFrame

def good_transform(data: DataFrame) -> DataFrame:
    """Pure transformation that accepts and returns DataFrame."""
    return data.filter("event_type = 'click'").select('user_id', 'ts')
```

## Key Takeaways

1. **DataFrame API first** - use RDDs only when absolutely necessary
2. **Separate I/O from transformations** - keep business logic pure and testable
3. **Single SparkSession** - create once in main, pass to functions that need it
4. **Structure code for testing** - organize into jobs/, etl/, tests/ hierarchy
5. **Cheap conversions** - switching between DataFrame and RDD is inexpensive when needed
