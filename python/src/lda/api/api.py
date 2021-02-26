from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import numpy as np
import psycopg2
import os


def get_dims():
    dims_query = "SELECT table_name, n FROM lda.dims"
    cur.execute(dims_query)
    res = cur.fetchall()
    return {x[0]: x[1] for x in res}


def query_data(args):
    dims = get_dims()
    keys = list(dims.keys())
    cache = [
        "INNER JOIN lda.{0} ON lda.{0}.id=lda.{1}.{0}_id_{2}".format(ne, la, args[ne])
        for ne, la in zip(keys[1:-1], keys[:-2])
    ]
    cache.append(
        "INNER JOIN lda.{0} ON ({1})".format(
            keys[-1],
            " OR ".join(
                [
                    "lda.{0}.id=lda.{1}.{0}_id_{2}".format(keys[-1], keys[-2], x)
                    for x in range(dims[keys[-1]])
                ]
            ),
        )
    )
    query = "SELECT lda.{0}.value FROM lda.{1} {2} WHERE lda.{1}.id={3}".format(
        keys[-1], keys[0], " ".join(cache), args[keys[0]]
    )

    try:
        cur.execute(query)
    except psycopg2.errors.InFailedSqlTransaction:
        cur.execute("ROLLBACK")
        connection.commit()
        cur.execute(query)
    return [0 if np.isnan(x[0]) else x[0] for x in cur.fetchall()]


app = Flask(__name__)
CORS(app)

load_dotenv()

connection = psycopg2.connect(
    user=os.getenv("POSTGRES_DB_USER"),
    password=os.getenv("POSTGRES_DB_PASSWORD"),
    host=os.getenv("POSTGRES_DB_HOST"),
    port=os.getenv("POSTGRES_DB_PORT"),
    dbname=os.getenv("POSTGRES_DB_NAME"),
)

cur = connection.cursor()


@app.route("/topicmodelling", methods=["GET"])
def topicmodelling():
    if request.method == "GET":
        return jsonify(
            {
                "data": [
                    {"x": 1949 + x, "y": y}
                    for x, y in enumerate(query_data(request.args))
                ]
            }
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5400)
