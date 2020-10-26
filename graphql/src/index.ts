import express = require("express");
import PgSimplifyInflectorPlugin from "@graphile-contrib/pg-simplify-inflector";
import { postgraphile } from "postgraphile";

import { SCHEMA_PUBLIC } from "./constants";
const ConnectionFilterPlugin = require("postgraphile-plugin-connection-filter");

const app = express();

app.use([
  postgraphile(
    {
      database: process.env.POSTGRES_DB_NAME,
      user: process.env.POSTGRES_DB_USER,
      password: process.env.POSTGRES_DB_PASSWORD,
      host: process.env.POSTGRES_DB_HOST,
      port: parseInt(process.env.POSTGRES_DB_PORT || "5432", 10),
    },
    SCHEMA_PUBLIC,
    {
      appendPlugins: [PgSimplifyInflectorPlugin, ConnectionFilterPlugin],
      graphileBuildOptions: {
        pgOmitListSuffix: true,
      },
      enableCors: true,
      watchPg: true,
      simpleCollections: "only",
      graphiql: true,
      enhanceGraphiql: true,
      dynamicJson: true,
    }
  ),
]);

app.listen(5000, "0.0.0.0");
