import flask_excel as excel


from . import views as report_view
from .models import CallTable, EventTable
from app import app


# Make excel responses
excel.init_excel(app)
