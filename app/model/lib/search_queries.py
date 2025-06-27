"""
This module contains the main function that performs the search query. In the
long run, it should be replaced by something that uses a full-text search and
is less complicated.
"""


def dynamical_query(all_advance_query):
    base_query = "SELECT DISTINCT publicId"
    search_final_query = ""
    values = []

    for query_dict in all_advance_query:
        where_clause = ""

        if not query_dict['option']:
            query_dict['option'] = 'Study Name'

        if query_dict['option'] == 'Project Name':
            project_name = query_dict['value'].strip().lower()
            if project_name != '':
                where_clause = f"""
                    FROM Studies
                    WHERE projectUuid IN (
                        SELECT uuid
                        FROM Projects
                        WHERE LOWER(name) LIKE :value_{len(values)}
                    )
                """
                values.append(f'%{project_name}%')
        elif query_dict['option'] == 'Project ID':
            project_id = query_dict['value'].strip()
            where_clause = f"""
                FROM Studies
                WHERE projectUuid IN (
                    SELECT uuid
                    FROM Projects
                    WHERE publicId = :value_{len(values)}
                )
            """
            values.append(project_id)
        elif query_dict['option'] == 'Study Name':
            study_name = query_dict['value'].strip().lower()
            where_clause = f"""
                FROM Studies
                WHERE LOWER(name) LIKE :value_{len(values)}
            """
            values.append(f"%{study_name}%")
        elif query_dict['option'] == 'Study ID':
            study_id = query_dict['value'].strip()
            where_clause = f"""
                FROM Studies
                WHERE publicId = :value_{len(values)}
            """
            values.append(study_id)
        elif query_dict['option'] == 'Microbial Strain':
            microb_strain = query_dict['value'].strip().lower()
            # Note: Creating a nested query so that "Strains.studyId" can be
            # renamed to "publicId"
            where_clause = f"""
            FROM (
                SELECT studyId as publicId, name, NCBId
                FROM Strains
            ) as Strains_Alias
            WHERE LOWER(name) LIKE :value_{len(values)}
            """
            values.append(f"%{microb_strain}%")
        elif query_dict['option'] == 'NCBI ID':
            microb_ID = query_dict['value'].strip()
            where_clause = f"""
            FROM (
                SELECT studyId as publicId, name, NCBId
                FROM Strains
            ) as Strains_Alias
            WHERE NCBId = :value_{len(values)}
            """
            values.append(microb_ID)
        elif query_dict['option'] == 'Metabolites':
            metabo = query_dict['value'].strip().lower()
            where_clause = f"""
                FROM (
                    SELECT
                        studyId as publicId,
                        Metabolites.name as name,
                        chebi_id
                    FROM StudyMetabolites
                    INNER JOIN Metabolites ON Metabolites.chebiId = StudyMetabolites.chebi_id
                ) as StudyMetabolites_Alias
                WHERE LOWER(name) LIKE :value_{len(values)}
            """
            values.append(f"%{metabo}%")
        elif query_dict['option'] == 'chEBI ID':
            chebi_id = query_dict['value'].strip()

            if not chebi_id.startswith('CHEBI:'):
                chebi_id = f"CHEBI:{chebi_id}"

            where_clause = f"""
                FROM (
                    SELECT
                        studyId as publicId,
                        Metabolites.name as name,
                        chebi_id
                    FROM StudyMetabolites
                    INNER JOIN Metabolites ON Metabolites.chebiId = StudyMetabolites.chebi_id
                ) as StudyMetabolites_Alias
                WHERE chebi_id = :value_{len(values)}
            """
            values.append(chebi_id)
        else:
            raise ValueError(f"Unknown option: {query_dict['option']}")

        logic_add = ""
        if 'logic_operator' in query_dict:
            if query_dict['logic_operator'] == 'AND':
                logic_add = " AND publicId IN ("
            if query_dict['logic_operator'] == 'OR':
                logic_add = " OR publicId IN ("
            if query_dict['logic_operator'] == 'NOT':
                logic_add = " AND publicId NOT IN ("

        if logic_add != "":
            final_query = logic_add + " " + base_query + " " + where_clause + " )"
        else:
            final_query = base_query + " " + where_clause + " "

        search_final_query += final_query

    search_final_query = search_final_query + ";"

    return search_final_query, values
