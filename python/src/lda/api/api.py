from flask import Flask, request, jsonify, g
from dotenv import load_dotenv
from flask_cors import CORS
from psycopg2 import pool
import numpy as np
import psycopg2
import os

constraints = None
dims = None
markers = {
    "topic_37": [
        {"axis": "x", "value": 1991, "legend": "Pariser Klimaabkommen"},
        {"axis": "x", "value": 1998, "legend": "Was anderes"},
    ],
    "topic_31": [
        {"axis": "x", "value": 1999, "legend": "Ganz wichtig"},
        {"axis": "x", "value": 2005, "legend": "Nicht so wichtig"},
    ],
    "topic_12": [
        {"axis": "x", "value": 1950, "legend": "Hier passiert was"},
    ],
}
annotations = [
    {
        "constraints": {"topics": "topic_37", "party": "party_2"},
        "index": 0,
        "annotation": {"title": "Nein", "description": "Doch", "otherprops": "Oh"},
    },
    {
        "constraints": {"topics": "topic_36", "party": "party_3"},
        "index": 8,
        "annotation": {"title": "Halloooo", "description": ":)"},
    },
    {
        "constraints": {"gender": "gender_1"},
        "index": 12,
        "annotation": {"title": "Miau", "description": "Wuff", "otherprops": "Grrr"},
    },
]


def get_constraints(schema, connection, cursor):
    global constraints
    query = """
        SELECT
            ccu.table_name,
            kcu.column_name
        FROM
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema='{0}';
        """.format(
        schema
    )
    try:
        cursor.execute(query)
    except psycopg2.errors.InFailedSqlTransaction:
        cursor.execute("ROLLBACK")
        connection.commit()
        cursor.execute(query)
    if constraints:
        constraints[schema] = {}
    else:
        constraints = {schema: {}}
    for res in cursor.fetchall():
        if res[0] in constraints[schema]:
            constraints[schema][res[0]].append(res[1])
        else:
            constraints[schema][res[0]] = [res[1]]
    return constraints


def get_dims(schema, connection, cursor):
    global dims
    dims_query = "SELECT table_name, n FROM {0}.dims".format(schema)
    try:
        cursor.execute(dims_query)
    except psycopg2.errors.InFailedSqlTransaction:
        cursor.execute("ROLLBACK")
        connection.commit()
        cursor.execute(dims_query)
    res = cursor.fetchall()
    if dims:
        dims[schema] = {x[0]: x[1] for x in res}
    else:
        dims = {schema: {x[0]: x[1] for x in res}}
    return dims


def get_db():
    if "db" not in g:
        g.db = app.config["postgreSQL_pool"].getconn()
    return g.db


def query_data(args, schema, connection, cursor):
    dim = (
        dims[schema]
        if dims and schema in dims
        else get_dims(schema, connection, cursor)[schema]
    )
    keys = list(dim.keys())
    cache = []
    format_string = "INNER JOIN " + schema + ".{0} ON {1}"
    for next_key, last_key in zip(keys[1:], keys[:-1]):
        if next_key in args:
            string = "{0}.{1}.id={0}.{2}.{3}".format(
                schema, next_key, last_key, args[next_key]
            )
        else:
            constraint = (
                constraints[schema][next_key]
                if constraints and schema in constraints
                else get_constraints(schema, connection, cursor)[schema][next_key]
            )
            string = (
                "("
                + " OR ".join(
                    [
                        "{0}.{1}.id={0}.{2}.{3}".format(schema, next_key, last_key, x)
                        for x in constraint
                    ]
                )
                + ")"
            )
        cache.append(format_string.format(next_key, string))
    query = "SELECT {0}.{1}.value, {0}.{1}.n FROM {0}.{2} {3} WHERE {0}.{2}.id='{4}'".format(
        schema, keys[-1], keys[0], " ".join(cache), args[keys[0]]
    )

    try:
        cursor.execute(query)
    except psycopg2.errors.InFailedSqlTransaction:
        cursor.execute("ROLLBACK")
        connection.commit()
        cursor.execute(query)
    data = [(0, x[1]) if np.isnan(x[0]) else (x[0], x[1]) for x in cursor.fetchall()]
    squashed_data = []
    for data_points in [data[i :: dim[keys[-1]]] for i in range(dim[keys[-1]])]:
        combined_weight = sum([data_point[1] for data_point in data_points])
        median = (
            0
            if combined_weight == 0
            else sum([data_point[0] * data_point[1] for data_point in data_points])
            / combined_weight
        )
        squashed_data.append(median)
    return squashed_data


app = Flask(__name__)

load_dotenv()

app.config["postgreSQL_pool"] = pool.SimpleConnectionPool(
    1,
    20,
    user=os.getenv("POSTGRES_DB_USER"),
    password=os.getenv("POSTGRES_DB_PASSWORD"),
    host=os.getenv("POSTGRES_DB_HOST"),
    port=os.getenv("POSTGRES_DB_PORT"),
    database=os.getenv("POSTGRES_DB_NAME"),
)

CORS(app)


@app.route("/topicmodelling", methods=["GET"])
def topicmodelling():
    db = get_db()
    cursor = db.cursor()
    if request.method == "GET":
        schema = "lda_person" if "politicians" in request.args else "lda_group"
        result = {
            "data": [
                {"x": 1949 + x, "y": y}
                for x, y in enumerate(query_data(request.args, schema, db, cursor))
            ],
            "markers": markers[request.args["topics"]]
            if "topics" in request.args and request.args["topics"] in markers
            else [],
        }
        for annotation in annotations:
            if (
                all(
                    [
                        constraint in request.args
                        and annotation["constraints"][constraint]
                        == request.args[constraint]
                        for constraint in annotation["constraints"]
                    ]
                )
                and len(result["data"]) > annotation["index"]
            ):
                result["data"][annotation["index"]]["annotation"] = annotation[
                    "annotation"
                ]
        return jsonify(result)
    cursor.close()


@app.teardown_appcontext
def close_conn(e):
    db = g.pop("db", None)
    if db is not None:
        app.config["postgreSQL_pool"].putconn(db)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5400)
