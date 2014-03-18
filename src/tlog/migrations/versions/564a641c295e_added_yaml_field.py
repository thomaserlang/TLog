"""added yaml field

Revision ID: 564a641c295e
Revises: 3c53f9f00049
Create Date: 2014-03-18 19:30:33.347000

"""

# revision identifiers, used by Alembic.
revision = '564a641c295e'
down_revision = '3c53f9f00049'

from alembic import op
import sqlalchemy as sa
from tlog.base.filter import Filters, Filter
import json
import yaml

def upgrade():
    op.add_column('filters',
        sa.Column('data_yaml', sa.Text)
    )
    op.add_column('filter_versions',
        sa.Column('data_yaml', sa.Text)
    )

    for f in Filters.get():
        Filter.update(
            id_=f.id,
            name=f.name,
            data_yaml=yaml.safe_dump(f.data),
        )

def downgrade():
    op.drop_column(
        'filters', 
        'data_yaml'
    )    
    op.drop_column(
        'filter_versions', 
        'data_yaml'
    )
