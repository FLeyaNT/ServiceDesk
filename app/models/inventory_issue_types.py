from sqlalchemy import (
    Table,
    Column,
    Integer,
    ForeignKey,
    PrimaryKeyConstraint
)

from .base_model import Base


inventory_issue_types = Table(
    'inventory_issue_types',
    Base.metadata,
    Column(
        'inventory_type_id',
        Integer,
        ForeignKey('inventory_types.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    ),
    Column(
        'issue_type_id',
        Integer,
        ForeignKey('issue_types.id', ondelete='CASCADE'),
        nullable=False
    ),
    PrimaryKeyConstraint(
        'inventory_type_id',
        'issue_type_id'
    )
)
