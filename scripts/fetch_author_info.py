import sqlalchemy as sql
import requests
import json

from app.model.orm import Study
from main import create_app
from db import FLASK_DB

app = create_app()

with app.app_context():
    db_session = FLASK_DB.session
    studies = db_session.scalars(
        sql.select(Study)
        .where(
            Study.url.is_not(None),
            Study.url != '',
        )
    )

    for study in studies:
        doi = study.url

        # Author records for linking and searching:
        crossref_url = f"https://api.crossref.org/works/{doi}"
        response = requests.get(crossref_url).json()

        if response["status"] != "ok":
            raise ValueError(f"Response was unsuccessful:\n{json.dumps(response, indent=2)}")

        study.authors = response.get("message", {}).get("author", [])

        # Citation:
        citation_url = f"https://citation.doi.org/format?doi={doi}&style=apa&lang=en-US"
        response = requests.get(citation_url).text.strip()
        study.citation = response

        print(response)

        db_session.add(study)

    db_session.commit()
