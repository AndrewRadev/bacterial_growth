# ORM Models

The application uses [SQLAlchemy](https://www.sqlalchemy.org/) for its ORM tools. Unfortunately, that's a large framework with a large amount of confusing documentation. In this guide, you can find an overview of how it's used in this project in particular.

## SQLAlchemy imports

In the app, SQLAlchemy is usually imported aliased to `sql`:

```python
import sqlalchemy as sql
```

There are a number of useful functions and types that are accessed through the main namespace:

- ORM query methods: `sql.select`, `sql.delete`
- ORM types: `sql.Integer`, `sql.String`, `sql.ForeignKey`
- Query functions: `sql.func.avg`, `sql.func.std`

In model classes, we might directly import names from `sqlalchemy.orm`, since in that context, it's clear that the names are used for database modeling:

```python
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
```

There are other imports for one-off types or functions, some of which will be shown later in this document.

## Basic ORM models

Each table in the database is represented in the code by an ORM model in the `app/model/orm/` directory. The table name is plural, while the model name is singular, and both are CapitalCamelCased. For example:

- The file `app/model/orm/bioreplicate.py` contains the model code
- There is only one class in it, called `Bioreplicate`, that inherits from `OrmBase`
- The table name is `Bioreplicates`

The file `app/model/orm/__init__.py` contains a full list of imports of *all* models, alphabetically sorted. Whenever any non-model file needs to import models, it should go through that file to ensure that all model code has been loaded *before* it gets evaluated. This avoids problems with uninitialized relationships. For instance, if you need to make a query that joins metabolites and their join table to studies, you might do something like this:

```python
from app.model.orm import (
    Bioreplicate,
    MeasurementContext,
)

# See the section "Fetching records" for an explanation on the following query:

bioreplicates = db_session.scalars(
    sql.select(Bioreplicate)
    .distinct()
    .join(MeasurementContext)
    .where(MeasurementContext.techniqueId == self.id)
).all()
```

If you need to reference other models in particular *model* file, it's highly recommended to perform this import inside the relevant method, rather than at the top of the file. That way, you avoid circular import errors. For instance, the above code was originally taken from inside a method in the `Measurement` model.

## Defining fields

The general formula for defining fields looks like this:

```
<field name>: Mapped[<python type>] = mapped_column(<SQL type>, <options>)
```

A few examples:

### Primary keys

```python
id:   Mapped[int] = mapped_column(primary_key=True)
uuid: Mapped[str] = mapped_column(sql.String(100), primary_key=True)
```

Note that the sql type is not mandatory, but is useful for documentation. It *might* be mandatory if you use a `bigint` field for an id, since SQLAlchemy seems to assume it's an integer and causes weird errors.

The primary key of the model doesn't necessarily need to be the same as the primary key of the table, though it's recommended to maintain consistency. Still, it could be useful to use a different column as a primary key temporarily for migration purposes.

### String fields

```python
name:        Mapped[str] = mapped_column(sql.String(100), nullable=False)
description: Mapped[str] = mapped_column(sql.String)
```

Providing a size can help with form validation. Flask-Admin uses wtforms to build forms with automatic maximum length etc by using this. Same for the nullability information. The convention in the project is that `VARCHAR` fields are given lengths in the model, while `TEXT` fields are not.

### Foreign keys

```python
dataFileId:   Mapped[int] = mapped_column(sql.ForeignKey('ExcelFiles.id'),        nullable=True)
experimentId: Mapped[str] = mapped_column(sql.ForeignKey('Experiments.publicId'), nullable=False)
```

A foreign key declaration is used by the relationships mechanism to automatically find the key that corresponds to a particular table. Note that the name in the `ForeignKey` call is a **table**, and not a model. The name is plural. If you mix this up, you could get some confusing errors.

The type of the key itself is not specified in the `mapped_column` call, but the type declaration determines whether it's `int` or `str`, or something else.

### JSON and BLOB fields

```python
studyDesign: Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)
content:     Mapped[bytes]    = mapped_column(sql.LargeBinary)
```

It's important to note that modifications to JSON fields will not be automatically persisted by the ORM, since changes are not tracked inside of the JSON data. When changing the insides of a JSON field, make sure to call `flag_modified` on the record with the name of the field:

```python
from sqlalchemy.orm.attributes import flag_modified

flag_modified(submission, 'studyDesign')
```

### Datetimes

```python
from sqlalchemy_utc.sqltypes import UtcDateTime

createdAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
```

Datetimes are handled using the external package [SQLAlchemy-Utc](https://pypi.org/project/SQLAlchemy-Utc/), because the built-in `DateTime` type doesn't play well with MySQL's `DATETIME` fields. Note the usage of `FetchedValue` -- this particular timestamp is set by MySQL, so SQLAlchemy is instructed not to give it a default value when creating or updating a record.

When setting timestamp values, make sure to create a timezone-aware python timestamp set to UTC:

```python
from datetime import datetime, UTC

study.publishedAt = datetime.now(UTC)
```

Python docs on "aware" and "naive" objects: <https://docs.python.org/3/library/datetime.html#aware-and-naive-objects>

## Defining relationships

SQLAlchemy documentation: <https://docs.sqlalchemy.org/en/20/orm/relationships.html>

Usually, it will be enough to use the `relationship` function with a `back_populates` key to define a relationship:

```python
experimentId: Mapped[str] = mapped_column(sql.ForeignKey('Experiments.publicId'), nullable=False)

experiment: Mapped['Experiment'] = relationship(back_populates='bioreplicates')
```

The `Mapped` declaration uses the name of the model as a string, because if it referred to the actual class, you would end up with circular dependency issues. SQLAlchemy resolves this string to a model name and errors out if it can't resolve all names after the loading process is complete.

### Foreign keys

The foreign key is necessary for the relationship to determine how to join to the other table. If there are multiple foreign keys defined to the same table or if there are no foreign keys, you can explicitly provide foreign keys as a parameter:

```python
from typing import Optional

oldCommunityId: Mapped[int] = mapped_column(sql.ForeignKey('Communities.id'))
newCommunityId: Mapped[int] = mapped_column(sql.ForeignKey('Communities.id'))

oldCommunity: Mapped[Optional['Community']] = relationship(foreign_keys=[oldCommunityId])
newCommunity: Mapped[Optional['Community']] = relationship(foreign_keys=[newCommunityId])
```

Note that the foreign keys are specified as actual python variables, since they are available within the context of the class declaration.

Also note the usage of `Optional` to describe that this relationship can resolve to `None`. This declaration is not mandatory, but once again, it's useful for Flask-Admin to apply the right validations in its forms.

### Inverse relationships, lists

The `back_populates` key is theoretically not necessary, but SQLAlchemy tends to error out when it's missing... Probably best to make sure each relationship is defined in both directions. On the other side, the experiment-bioreplicates relationship is a `List`:

```python
class Bioreplicate(OrmBase):
    # ...

    experimentId: Mapped[str] = mapped_column(sql.ForeignKey('Experiments.publicId'), nullable=False)
    experiment: Mapped['Experiment'] = relationship(back_populates='bioreplicates')
```

```python
from typing import List

class Experiment(OrmBase):
    # ...

    bioreplicates: Mapped[List['Bioreplicate']] = relationship(
        order_by='Bioreplicate.calculationType.is_(None), Bioreplicate.id',
        back_populates='experiment',
        cascade='all, delete-orphan'
    )
```

There are two new keys here. The `order_by` includes an SQLAlchemy expression that determines the ordering.

The `cascade` one is more important. This clause is in the model `Experiment`. When an experiment is deleted, or its `bioreplicates` field is mutated, the `cascade='all, delete-orphan'` clause ensures that the "orphaned" bioreplicates get deleted as well. Without this clause, the default behaviour is to nullify the `experimentId` field, and if that one is declared to be non-null, this will be a database error that is hard to debug. It'll be reported as an SQL error when updating a model, with zero detail on what field, exactly, the was problem in.

It's important to carefully consider which model is the "owner" of another model that will result in destroying other related records. It's not a good idea to just put this clause everywhere, or we'll end up accidentally deleting records that we care about.

As a side note, the join key is on the Bioreplicate model, it's not necessary to declare it in the inverse relationship.

### Join tables

To join a model through a different model, you can use the `secondary` key:

```python
class Bioreplicate(OrmBase):
    # ...

    measurementContexts: Mapped[List['MeasurementContext']] = relationship(
        back_populates='bioreplicate',
        cascade='all, delete-orphan'
    )
```

```python
class MeasurementContext(OrmBase):
    # ...

    bioreplicateId: Mapped[int] = mapped_column(sql.ForeignKey('Bioreplicates.id'))
    bioreplicate: Mapped['Bioreplicate'] = relationship(back_populates='measurementContexts')
```

```python
class Measurement(OrmBase):
    # ...

    contextId: Mapped[int] = mapped_column(sql.ForeignKey('MeasurementContexts.id'))
    context: Mapped['MeasurementContext'] = relationship(back_populates='measurements')
```


We have a direct relationship between `Bioreplicate` and `MeasurementContext`: The latter class has a `bioreplicateId` key and a `bioreplicate` relationship. Its child `Measurement` class has a `contextId` key and a `context` relationship. We have `Bioreplicate -> List[MeasurementContext] -> List[Measurement]`.

Or, in terms of database tables and keys:
- `Measurements.contextId -> MeasurementContexts.id`
- `MeasurementContexts.bioreplicateId -> Bioreplicates.id`

With this, we can add a "secondary" relationship directly from bioreplicates to measurements:

```python
class Bioreplicate(OrmBase):
    # ...

    measurements: Mapped[List['Measurement']] = relationship(
        order_by='Measurement.timeInSeconds',
        secondary='MeasurementContexts',
        viewonly=True,
    )
```

The "secondary" table is the join table that we go through. Note that it's a **table** and not a model, so its name is plural. If you mix these up, you'll run into confusing errors. It's also important to specify `viewonly=True`. SQLAlchemy doesn't just define relationships for reading, but also exposes them as lists that can be mutated. It is technically impossible, however, to add measurements directly to `bioreplicate.measurements`, since we would be unable to describe the missing context between them.

This is why this has to be read-only relationship, allowing us to easily query it with a join through the intermediate table, but preventing us from trying to mutate it.

## Fetching records

To fetch records from the database, we need an SQLAlchemy `Session` object. In page handlers, one will be available to the application as `g.db_session`. In tests, it will be initialized per-test in the `self.db_session` property, as long as the test inherits `DatabaseTest`. To initialize a session directly, you can call the function `get_session` in the `db` module:

```python
from db import get_session

with get_session() as db_session:
    # ...
```

### Single record

The simplest way to fetch a record by primary key is by using the `get` method:

```python
from models import Study

study = g.db_session.get(Study, '<primary key>')

print(study.name)
# "Synthetic human gut bacterial community using an automated fermentation system"
```

The method `.get` returns `None` if there is no record with that primary key, but you can call `.get_one` to raise an error if the record is not found. In the app, this particular exception is caught and renders a 404.

To fetch a study by an arbitrary query, we can use the `.scalars` method that returns a result, and then call `.one()` on it to fetch a single result or `.one_or_none()` to allow the method to return nothing:

```python
import sqlalchemy as sql
from models import Study

study = g.db_session.scalars(
    sql.select(Study)
    .where(Study.studyId == 'SMGDB00000001')
    .limit(1)
).one_or_none()

print(study.name)
# "Synthetic human gut bacterial community using an automated fermentation system"
```

We don't *have* to add `.limit(1)` to the query, but it's not a bad idea to avoid extra work by the database.

Annoyingly, the naming convention between `.get()` and `.one()` is different when it comes to errors. When a record is missing:

- `.get()` returns None, while `.get_one()` raises an error
- `.one()` raises an error, while `.one_or_none()` returns None

This can be confusing, but it is what it is. When it doubt, consider writing a test that describes the expected behaviour, both for your own certainty and for future developers.

### Multiple records

To fetch a list of records, we can use the same query, but invoke `.all()` on the result, instead of `.one()`.

```python
import sqlalchemy as sql
from models import Study

studies = g.db_session.scalars(
    sql.select(Study)
    .limit(2)
).all()

print(len(studies))
# 2
```

The `.scalars` method simply tells the session to return a single item for each found result. If you want to select one field of the model, you can use that instead:

```python
import sqlalchemy as sql
from models import Study

study_ids = g.db_session.scalars(
    sql.select(Study.studyId)
    .limit(2)
).all()

print(study_ids)
# ['SMGDB00000001', 'SMGDB00000002']
```

Be careful: if you add multiple fields in the `select` clause, the `scalars` method will give you a flat list of the selected fields which doesn't seem like a particularly useful result.

### Specific columns

To query for a collection of fields and get tuples as results, we can use the `execute` method on the session, followed by an invocation of `.all()`:

```python
measurement_rows = g.db_session.execute(
    sql.select(
        Measurement.timeInSeconds,
        sql.func.avg(Measurement.value),
        sql.func.std(Measurement.value),
    )
    .where(Measurement.contextId.in_([mc.id for mc in measurement_contexts]))
    .group_by(Measurement.timeInSeconds)
    .order_by(Measurement.timeInSeconds)
).all()

for (time, value, std) in measurement_rows:
    # ...
```

In the `app.model.lib.db` module there is a utility function called `execute_into_df` that gives you a pandas dataframe with the result, which can be particularly useful for tabular data. In the app, it's mostly used for charts or for CSV exports.

### In migrations

We don't want to rely on models inside of database migrations, because the code and the database may not have the same state while the migration is being run. We use a "connection" object instead and call `execute` with textual queries:

```python
query = """
    ALTER TABLE Users
    MODIFY orcidToken VARCHAR(100) DEFAULT NULL
"""
conn.execute(sql.text(query))
```

If we need to provide parameters, we can do this with the second argument to `execute`:

```python
query = f"""
    UPDATE Bioreplicates
    SET experimentId = :public_id
    WHERE deprecatedExperimentId = :id
"""
conn.execute(sql.text(query), {
    'id': deprecated_experiment_id,
    'public_id': experiment_public_id,
})
```

In migrations, we'd usually not use the result of the query, but we can call `.scalars()` on it to get single result values, call `.all()` to get multiple rows or `.one()` to get a single row.

```python
experiment_public_id = conn.execute(
    sql.text("SELECT publicId FROM Experiments WHERE id = :id"),
    {'id': deprecated_experiment_id},
).scalars().one()
```

## Creating or updating records

## Specific recipes

In this section, we'll list some special use cases that you might find in one or two places in the codebase and might not be particularly obvious.

### JSON fields

If a model has a JSON field, then modifying it will not flag the model as needing to be changed. You need to call `flag_modified`:

```python
from sqlalchemy.orm.attributes import flag_modified

submission = g.db_session.get(Submission, 42)

submission.studyDesign['project']['name'] = 'Updated'
flag_modified(submission)

g.db_session.add(submission)
g.db_session.commit()
```

If you forget to invoke that function, SQLAlchemy will happily "forget" to invoke an SQL query. This is unfortunate, but it seems unavoidable.

### Hybrid properties

Flask documentation: [Hybrid Attributes](https://docs.sqlalchemy.org/en/20/orm/extensions/hybrid.html)

These properties are a little bit weird. The idea is that a single method or property name can represent the same thing on both the *instance* level and on the *class* level.

As an example, suppose we have a hybrid property `isPublishable`:

```python
class Study:
    # ...

    @hybrid_property
    def isPublishable(self):
        return self.publishableAt and self.publishableAt <= datetime.now(UTC)
```

If we have a particular study object, then within `study.isPublishable`, the value `self.publishedAt` will be a specific timestamp and the result of the function will be the comparison of the timestamp with `datetime.now(UTC)`. It'll return either `True` or `False` depending on the particular object that we have.

However, if we access the class-level property `Study.isPublishable`, the value `self.publishedAt` will be a *column object* that represents this entire database column. The expression `self.publishableAt` will always be a truthy value, and `self.publishableAt <= datetime.now(UTC)` will get translated to an SQL query fragment:

```python
from models import Study
import sqlalchemy as sql

print(sql.select(Study).where(Study.isPublishable))
```

The query that gets printed is:

```
SELECT "Study"."studyUniqueID", "Study"."studyId", "Study"."studyName", "Study"."studyDescription", "Study"."studyURL", "Study"."timeUnits", "Study"."projectUniqueID", "Study"."createdAt", "Study"."updatedAt", "Study"."publishableAt", "Study"."publishedAt", "Study"."embargoExpiresAt"
FROM "Study"
WHERE "Study"."publishableAt" <= :publishableAt_1
```

The template `:publishableAt_1` is going to be interpolated with the value of `datetime.now(UTC)` at the time the function was invoked.

This is convenient to give a simple name to a computed expression, valid on both individual objects and for database queries, but it might be impractical if the expression is too complicated. The full documentation describes how to define *different* behaviour at the class and instance level, but at this time, the codebase doesn't make use of that to avoid unnecessary complexity.
