import numpy as np
import pandas as pd
import psycopg2

import open_discourse.definitions.path_definitions as path_definitions


def upload_dims(cur, dims, shape, schema):
    cur.execute(
        "CREATE TABLE IF NOT EXISTS {0}.dims(id serial NOT NULL, table_name varchar NOT NULL, n int8 NOT NULL, CONSTRAINT dims_pk PRIMARY KEY (id));".format(
            schema
        )
    )

    for table_name, n in zip(dims, shape):
        cur.execute(
            "INSERT INTO {0}.dims (table_name, n) VALUES (%s, %s)".format(schema),
            (table_name, n),
        )


def create_tables(cur, dims, schema):
    dims_keys = list(dims.keys())
    cur.execute(
        "CREATE TABLE IF NOT EXISTS {0}.{1}(id int8 NOT NULL, value double precision NULL, n int8 NULL, CONSTRAINT {1}_pk PRIMARY KEY (id));".format(
            schema, dims_keys[-1]
        )
    )

    for current_dimension, next_dimension in zip(
        dims_keys[1:-1][::-1], dims_keys[2:][::-1]
    ):
        keys = [x[0] for x in dims[next_dimension]]
        parsed_fields = ["{0} int8 NOT NULL,".format(dim) for dim in keys]
        parsed_foreign_keys = [
            "CONSTRAINT {0}_fk_{1} FOREIGN KEY ({2}) REFERENCES {3}.{4}(id),".format(
                current_dimension, dim, key, schema, next_dimension
            )
            for dim, key in enumerate(keys)
        ]
        cur.execute(
            "CREATE TABLE IF NOT EXISTS {0}.{1}(id int8 NOT NULL, {2}{3}CONSTRAINT {1}_pk PRIMARY KEY (id));".format(
                schema,
                current_dimension,
                "".join(parsed_fields),
                "".join(parsed_foreign_keys),
            )
        )
    keys = [x[0] for x in dims[dims_keys[1]]]
    parsed_fields = ["{0} int8 NOT NULL,".format(dim) for dim in keys]
    parsed_foreign_keys = [
        "CONSTRAINT {0}_fk_{1} FOREIGN KEY ({2}) REFERENCES {3}.{4}(id),".format(
            dims_keys[0], dim, key, schema, dims_keys[1]
        )
        for dim, key in enumerate(keys)
    ]
    cur.execute(
        "CREATE TABLE IF NOT EXISTS {0}.{1}(id varchar NOT NULL, {2}{3}CONSTRAINT {1}_pk PRIMARY KEY (id));".format(
            schema,
            dims_keys[0],
            "".join(parsed_fields),
            "".join(parsed_foreign_keys),
        )
    )


def recursive_upload(cur, data_cube, weight_cube, dims, counter, depth, schema):
    dims_keys = list(dims.keys())
    for data_elem, weight_elem in zip(data_cube, weight_cube):
        if len(dims) == 1:
            cur.execute(
                "INSERT INTO {0}.{1} (id, value, n) VALUES (%s, %s, %s)".format(
                    schema, dims_keys[0]
                ),
                (counter[len(dims) - 1], data_elem, weight_elem),
            )
        else:
            recursive_upload(
                cur,
                data_elem,
                weight_elem,
                {x: dims[x] for x in dims_keys[1:]},
                counter,
                depth + 1,
                schema,
            )
            parsed_fields = [x[0] for x in dims[dims_keys[1]]]
            format_string = ["%s"] * (len(parsed_fields) + 1)
            cur.execute(
                "INSERT INTO {0}.{1} (id, {2}) VALUES ({3})".format(
                    schema,
                    dims_keys[0],
                    ",".join(parsed_fields),
                    ",".join(format_string),
                ),
                (
                    dims[dims_keys[0]][int(counter[len(dims) - 1])][0]
                    if depth == 0
                    else int(counter[len(dims) - 1]),
                    *range(
                        int(counter[len(dims) - 2]) - int(data_elem.shape[0]),
                        int(counter[len(dims) - 2]),
                    ),
                ),
            )
        counter[len(dims) - 1] += 1


conn = psycopg2.connect(
    dbname="next", user="postgres", password="postgres", host="localhost"
)
cur = conn.cursor()


data_cube = pd.read_pickle(path_definitions.FINAL / "data_cube.pkl")
weight_cube = pd.read_pickle(path_definitions.FINAL / "weight_cube.pkl")
dims = pd.read_pickle(path_definitions.FINAL / "dims.pkl")
shape = data_cube.shape
schema = "lda_group"

upload_dims(cur, dims, shape, schema)
conn.commit()

create_tables(cur, dims, schema)
conn.commit()

recursive_upload(
    cur,
    data_cube,
    weight_cube,
    dims,
    np.zeros(len(dims)),
    0,
    schema,
)
conn.commit()


data_cube = pd.read_pickle(path_definitions.FINAL / "politician_data_cube.pkl")
weight_cube = pd.read_pickle(path_definitions.FINAL / "politician_weight_cube.pkl")
dims = pd.read_pickle(path_definitions.FINAL / "politician_dims.pkl")
shape = data_cube.shape
schema = "lda_person"

upload_dims(cur, dims, shape, schema)
conn.commit()

create_tables(cur, dims, schema)
conn.commit()

recursive_upload(cur, data_cube, weight_cube, dims, np.zeros(len(dims)), 0, schema)
conn.commit()

cur.close()
conn.close()
