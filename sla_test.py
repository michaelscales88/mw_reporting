from app.report.core import cache, sla_report
from app.report import CallTable
from datetime import datetime
from sqlalchemy.sql import func
from app import app
from app.database import db_session

date = datetime.today().replace(day=5).date()

query = db_session.query(CallTable).filter(func.date(date))

# Cache consumes the events relationship of each CallTable
# Returns a list of key value pairs CallTable: (Summary of EventsTable)
cached_records = cache(query.all())

# for record, cached_events in cached_records.items():
#     print(record)
#     print(cached_events.items())

# Run report on cached records
results = sla_report(cached_records, list(app.config['CLIENTS']))
print(results)
