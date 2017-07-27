from app.database import sessionmaker, scoped_session, create_engine
from app import app
from app.report.core import results_to_dict


engine = create_engine(app.config['MSSQL_CONNECTION'])
print(engine)
session = sessionmaker(bind=engine)
Session = scoped_session(session)
src_session = Session()
statement = """SELECT DISTINCT TOP 10 bug_posts.bp_bug FROM bug_posts"""
q1 = src_session.execute(statement)
zipped = results_to_dict(q1)
for zipd in zipped:
    print(zipd)
