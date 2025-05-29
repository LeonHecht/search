# Copyright 2025 Leon Hecht
# Licensed under the Apache License, Version 2.0 (see LICENSE file)

from sqlmodel import Session, select
from app.db import engine
from app.models.query_log import QueryLog
from app.models.feedback import Feedback


def show_all_data() -> None:
    """
    Print out everything in the QueryLog and Feedback tables
    for a quick sanity check.
    """
    with Session(engine) as sess:
        logs = sess.exec(select(QueryLog)).all()
        feedbacks = sess.exec(select(Feedback)).all()

    print("=== QueryLog ===")
    for l in logs:
        print(l)
    print("\n=== Feedback ===")
    for f in feedbacks:
        print(f)


if __name__ == "__main__":
    show_all_data()
