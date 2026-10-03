# DB201 Databases - Lecture Notes

## Relational model
Data lives in tables (relations) with rows and typed columns. Primary keys identify rows; foreign keys link tables.

## SQL joins
INNER JOIN keeps matching rows only. LEFT JOIN keeps all left rows plus matches. Joins on unindexed columns are slow.

## Normalization
1NF: atomic values. 2NF: no partial dependency on a composite key. 3NF: no transitive dependency.
Normalize to avoid update anomalies; denormalize deliberately for read speed.

## Transactions and ACID
Atomicity, Consistency, Isolation, Durability. Isolation levels trade correctness against concurrency.
