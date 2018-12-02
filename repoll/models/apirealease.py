from .meta import Base
import datetime
from sqlalchemy import (Column, Integer, Unicode,
                        UnicodeText, DateTime, ForeignKey, 
                        String)




class APIRelease(Base):
	__tablename__ = 'apirelease'
	buildtime = Column(DateTime, default=datetime.datetime.utcnow())
	version = Column(String, primary_key=True)
	links = Column(String)
	methods = Column(String)
