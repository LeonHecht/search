# Copyright 2025 Leon Hecht
# Licensed under the Apache License, Version 2.0 (see LICENSE file)

from sqlmodel import SQLModel, create_engine

# import every model so SQLModel.metadata knows about them
from app.models.query_log import QueryLog
from app.models.feedback  import Feedback


engine = create_engine("sqlite:///./queries.db", echo=False)
SQLModel.metadata.create_all(engine)