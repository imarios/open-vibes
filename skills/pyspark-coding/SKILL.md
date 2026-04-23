---
name: pyspark-coding
description: Use this skill when writing PySpark code. Provides PySpark best practices for manageability, testability, and performance including DataFrame patterns, caching strategies, testing approaches, and deployment configurations.
version: 1.0.0
---

# PySpark Coding Guidelines

Comprehensive PySpark development practices for manageability, testability, and high performance.

## When to Use This Skill

Use this skill when:
- Writing PySpark data processing jobs
- Optimizing PySpark performance and reducing compute costs
- Testing PySpark transformations and jobs
- Deciding between DataFrame API and RDD API
- Configuring Spark for local development or cluster deployment
- Implementing caching and persistence strategies

## Reference Routing Table

| Reference | Read when you need to… |
|-----------|------------------------|
| `fundamentals.md` | Start a new PySpark project — DataFrame vs RDD decision, code structure, testability patterns, SparkSession management |
| `performance.md` | Optimize PySpark jobs — caching/persistence strategies, join optimization, partitioning, file format choices, I/O patterns |
| `testing-and-deployment.md` | Set up PySpark testing — local dev vs cluster configs, parallelism tuning, executor settings, deployment practices |
