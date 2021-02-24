import lda.definitions.path_definitions as path_definitions
import pandas as pd
import numpy as np
import psycopg2
import os


def recursive_upload(data_cube, weight_cube, dims, counter):
    for data_elem, weight_elem in zip(data_cube, weight_cube):
        if len(dims) == 1:
            cur.execute(
                "INSERT INTO lda.{0} (id, value, n) VALUES (%s, %s, %s)".format(
                    dims[0]
                ),
                (counter[len(dims) - 1], data_elem, weight_elem),
            )
        else:
            recursive_upload(data_elem, weight_elem, dims[1:], counter)
            parsed_fields = [
                "{0}_id_{1}".format(dims[1], dim) for dim in range(data_elem.shape[0])
            ]
            format_string = ["%s"] * (len(parsed_fields) + 1)
            cur.execute(
                "INSERT INTO lda.{0} (id, {1}) VALUES ({2})".format(
                    dims[0], ",".join(parsed_fields), ",".join(format_string)
                ),
                (
                    int(counter[len(dims) - 1]),
                    *range(
                        int(counter[len(dims) - 2]) - int(data_elem.shape[0]),
                        int(counter[len(dims) - 2]),
                    ),
                ),
            )
        counter[len(dims) - 1] += 1


data_cube = pd.read_pickle(os.path.join(path_definitions.FINAL, "data_cube.pkl"))
weight_cube = pd.read_pickle(os.path.join(path_definitions.FINAL, "weight_cube.pkl"))
dims = list(pd.read_pickle(os.path.join(path_definitions.FINAL, "dims.pkl")).keys())

conn = psycopg2.connect(
    dbname="next", user="postgres", password="postgres", host="localhost"
)
cur = conn.cursor()

shape = data_cube.shape
cur.execute(
    "CREATE TABLE lda.{0}(id int8 NOT NULL, value double precision NULL, n int8 NULL, CONSTRAINT {0}_pk PRIMARY KEY (id));".format(  # noqa: E501
        dims[-1]
    )
)
for current_dimension, next_dimension, next_shape in zip(
    dims[:-1][::-1], dims[1:][::-1], shape[1:][::-1]
):
    parsed_fields = [
        "{0}_id_{1} int8 NOT NULL,".format(next_dimension, dim)
        for dim in range(next_shape)
    ]
    parsed_foreign_keys = [
        "CONSTRAINT {0}_fk_{1} FOREIGN KEY ({2}_id_{1}) REFERENCES lda.{2}(id),".format(
            current_dimension, dim, next_dimension
        )
        for dim in range(next_shape)
    ]
    cur.execute(
        "CREATE TABLE lda.{0}(id int8 NOT NULL, {1}{2}CONSTRAINT {0}_pk PRIMARY KEY (id));".format(
            current_dimension, "".join(parsed_fields), "".join(parsed_foreign_keys)
        )
    )
conn.commit()

recursive_upload(data_cube, weight_cube, dims, np.zeros(len(dims)))
conn.commit()

cur.close()
conn.close()
