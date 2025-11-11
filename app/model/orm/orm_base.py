from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.inspection import inspect
import sqlalchemy as sql


class OrmBase(DeclarativeBase):
    "The shared base class of all the ORM models"

    @classmethod
    def filter_keys(Self, data: dict):
        return {k: v for k, v in data.items() if hasattr(Self, k)}

    @classmethod
    def list_ordering(Self, column, values):
        """
        Return an sql CASE statement that can be used to order records based on
        the values of this column according to the given list of values.
        """
        cases = []

        for i, entry in enumerate(values):
            cases.append((column == entry, i))

        return sql.case(*cases, else_=len(cases))

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def _asdict(self):
        return {
            c.name: "<BLOB>" if isinstance(c.type, sql.LargeBinary) else getattr(self, c.name)
            for c in inspect(type(self)).c
        }

    def __str__(self):
        parts = []

        if hasattr(self, 'id'):
            parts.append(f"id={self.id}")
        if hasattr(self, 'publicId'):
            parts.append(f"publicId={self.publicId}")

        return f"<{type(self).__name__} {', '.join(parts)}>"

    def __repr__(self):
        name = type(self).__name__
        props = ', '.join([f"{k}={repr(v)}" for k, v in self._asdict().items()])

        return f"{name}({props})"

    def _validate_inclusion(self, key, value, valid_values):
        if value not in valid_values:
            raise ValueError(f"Invalid value for {key}: {repr(value)}, must be one of {repr(valid_values)}")

        return value
