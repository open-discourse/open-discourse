import { Pool, PoolClient } from "pg";
import express = require("express");
import puppeteer from "puppeteer";
import mcache from "memory-cache";
import { v4 } from "uuid";
import AWS from "aws-sdk";
import cors from "cors";

const zip = (arr: any[], ...arrs: any[]): any[] => {
  return arr.map((val, i) => arrs.reduce((a, arr) => [...a, arr[i]], [val]));
};

const app = express();

app.use(cors());

const pool = new Pool({
  user: process.env.POSTGRES_DB_USER || "postgres",
  host: process.env.POSTGRES_DB_HOST || "localhost",
  database: process.env.POSTGRES_DB_NAME || "next",
  password: process.env.POSTGRES_DB_PASSWORD || "postgres",
  port: process.env.POSTGRES_DB_PORT
    ? parseInt(process.env.POSTGRES_DB_PORT)
    : 5432,
});

const pool2 = process.env.POSTGRES_PERSISTENT_DB_HOST
  ? new Pool({
      user: process.env.POSTGRES_PERSISTENT_DB_USER || "postgres",
      host: process.env.POSTGRES_PERSISTENT_DB_HOST || "localhost",
      database: process.env.POSTGRES_PERSISTENT_DB_NAME || "open_discourse",
      password: process.env.POSTGRES_PERSISTENT_DB_PASSWORD || "postgres",
      port: process.env.POSTGRES_PERSISTENT_DB_PORT
        ? parseInt(process.env.POSTGRES_PERSISTENT_DB_PORT)
        : 2345,
    })
  : undefined;

const cache = (duration: number) => {
  return (
    req: express.Request,
    res: express.Response,
    next: express.NextFunction
  ) => {
    const key = "__express__" + req.originalUrl || req.url;
    if ((req.originalUrl || req.url).startsWith("/?")) {
      (
        pool2 ?? pool
      ).query(`INSERT INTO misc.fts_tracking (search_query) VALUES ($1)`, [
        req.originalUrl || req.url,
      ]);
    }

    const cachedBody = JSON.parse(mcache.get(key));
    if (cachedBody) {
      res.send(cachedBody);
      return;
    } else {
      const originalSend = res.send.bind(res);
      res.send = (body) => {
        mcache.put(key, body, duration * 1000);
        return originalSend(body);
      };
      next();
    }
  };
};

app.get(
  "/",
  cache(((process.env.CACHE_EXPIRATION as unknown) as number) || 1),
  async function (req, res) {
    const {
      query: {
        contentQuery,
        factionIdQuery,
        fromDate,
        toDate,
        politicianIdQuery,
        positionShortQuery,
      },
    } = req;
    const result = await pool.query(
      `SELECT id, position_short AS "positionShort", date, speech_content AS "speechContent", document_url AS "documentUrl", rank,
              first_name AS "firstName", last_name AS "lastName", abbreviation
       FROM open_discourse.search_speeches($1, $2, $3, $4, $5, $6) LIMIT $7`,
      [
        politicianIdQuery ? ((politicianIdQuery as unknown) as number) : -2,
        factionIdQuery ? ((factionIdQuery as unknown) as number) : -2,
        positionShortQuery || "",
        contentQuery || "",
        fromDate,
        toDate,
        process.env.QUERY_LIMIT || "50",
      ]
    );
    res.setHeader("Content-Type", "application/json");
    res.send({ data: { searchSpeeches: result.rows } });
  }
);

app.get(
  "/politicians",
  cache(((process.env.CACHE_EXPIRATION as unknown) as number) || 1),
  async (_req, res) => {
    const result = await pool.query(
      'SELECT id, first_name AS "firstName", last_name AS "lastName" FROM open_discourse.politicians'
    );
    res.setHeader("Content-Type", "application/json");
    res.send(JSON.stringify({ data: { politicians: result.rows } }));
  }
);

app.get(
  "/factions",
  cache(((process.env.CACHE_EXPIRATION as unknown) as number) || 1),
  async (_req, res) => {
    const result = await pool.query(
      'SELECT id, full_name AS "fullName", abbreviation FROM open_discourse.factions'
    );
    res.setHeader("Content-Type", "application/json");
    res.send(JSON.stringify({ data: { factions: result.rows } }));
  }
);

interface argsType {
  [key: string]: string;
}

interface dimsType {
  [schema: string]: { [property: string]: number };
}

interface constraintsType {
  [schema: string]: { [property: string]: string[] };
}

let dims: dimsType = {};
let constraints: constraintsType = {};

const getConstraints = async (
  schema: string,
  client: PoolClient
): Promise<constraintsType> => {
  const res = await client.query(`SELECT
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
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema='${schema}';`);
  if (!(schema in constraints)) {
    constraints[schema] = {};
  }
  for (let part of res.rows as { [property: string]: string }[]) {
    if (part["table_name"] in constraints[schema]) {
      constraints[schema][part["table_name"]].push(part["column_name"]);
    } else {
      constraints[schema][part["table_name"]] = [part["column_name"]];
    }
  }
  return constraints;
};

const getDims = async (
  schema: string,
  client: PoolClient
): Promise<dimsType> => {
  const res = await client.query(`SELECT table_name, n FROM ${schema}.dims`);
  dims[schema] = Object.fromEntries(
    res.rows.map((element) => [element["table_name"], +element["n"]])
  );
  return dims;
};

const queryData = async (
  args: argsType,
  schema: string,
  client: PoolClient
): Promise<number[]> => {
  const dim =
    schema in dims ? dims[schema] : (await getDims(schema, client))[schema];
  const keys = Object.keys(dim);
  let cache = [];
  for (let tuple of zip(keys.slice(1), keys.slice(0, -1))) {
    const nextKey = tuple[0] as string;
    const lastKey = tuple[1] as string;
    if (nextKey in args) {
      cache.push(
        `INNER JOIN ${schema}.${nextKey} ON ${schema}.${nextKey}.id=${schema}.${lastKey}.${args[nextKey]}`
      );
    } else {
      const constraint =
        schema in constraints
          ? constraints[schema][nextKey]
          : (await getConstraints(schema, client))[schema][nextKey];
      cache.push(
        `INNER JOIN ${schema}.${nextKey} ON (${constraint
          .map(
            (element) =>
              `${schema}.${nextKey}.id=${schema}.${lastKey}.${element}`
          )
          .join(" OR ")})`
      );
    }
  }
  const res = await client.query(
    `SELECT ${schema}.${keys[keys.length - 1]}.value, ${schema}.${
      keys[keys.length - 1]
    }.n FROM ${schema}.${keys[0]} ${cache.join(" ")} WHERE ${schema}.${
      keys[0]
    }.id=$1`,
    [args[keys[0]]]
  );
  const data = res.rows.map((element) =>
    isNaN(element.value) ? [0, +element.n] : [element.value, +element.n]
  );
  const dataPoints = [
    ...Array(dim[keys[keys.length - 1]]).keys(),
  ].map((firstIndex) =>
    data.filter(
      (_, secondIndex) => secondIndex % dim[keys[keys.length - 1]] == firstIndex
    )
  );
  return dataPoints.map((element) => {
    const combined_weight = element.reduce((acc, el) => acc + el[1], 0);
    return combined_weight
      ? element.reduce((acc, el) => acc + el[0] * el[1], 0) / combined_weight
      : 0;
  });
};

interface markerType {
  [proptery: string]: { axis: string; value: number; legend: string }[];
}
interface annotationType {
  constraints: { [property: string]: string };
  index: number;
  annotation: { title: string; description: string; otherprops?: string };
}

const markers: markerType = {};

const annotations: annotationType[] = [];

interface dataType {
  x: number;
  y: number;
  annotation?: { title: string; description: string; otherprops?: string };
}

app.get(
  "/topicmodelling",
  cache(((process.env.CACHE_EXPIRATION as unknown) as number) || 1),
  async (req, res) => {
    const client = await pool.connect();
    try {
      const schema = "politicians" in req.query ? "lda_person" : "lda_group";
      let result = {
        data: (await queryData(req.query as argsType, schema, client)).map(
          (y, x) => ({
            x: 1949 + x,
            y: y,
          })
        ) as dataType[],
        markers:
          "topics" in req.query && (req.query["topics"] as string) in markers
            ? markers[req.query["topics"] as string]
            : [],
      };
      annotations
        .filter((element) =>
          Object.keys(element.constraints)
            .map(
              (constraint) =>
                constraint in req.query &&
                element.constraints[constraint] == req.query[constraint]
            )
            .every(Boolean)
        )
        .map(
          (element) =>
            (result.data[element.index].annotation = element.annotation)
        );
      res.setHeader("Content-Type", "application/json");
      res.send(JSON.stringify(result));
    } finally {
      client.release();
    }
  }
);

app.get(
  "/screenshot",
  cache(((process.env.CACHE_EXPIRATION as unknown) as number) || 1),
  async (req, res) => {
    const {
      query: { url, selector },
    } = req;
    const random_id = v4();
    if (!url) {
      res.status(400).send(JSON.parse(`{"error": "Missing url parameter"}`));
      return;
    }
    res.send(JSON.parse(`{"fileName": "${random_id}.jpg"}`));
    const { host } = new URL(url as string);
    const split_host = host.split(".");
    if (
      split_host.slice(-2).join(".") != "opendiscourse.de" &&
      split_host.slice(-3).join(".") != "ofranke.vercel.app" &&
      split_host.slice(-1).join(".") != "localhost"
    ) {
      throw Error("Bad URL Name");
    }
    const browser = await puppeteer.launch({
      args: ["--no-sandbox"],
    });
    const page = await browser.newPage();
    page.setViewport({ width: 1920, height: 800, deviceScaleFactor: 1 });
    await page.goto(url as string, {
      waitUntil: "networkidle2",
    });
    const imageBuffer = await screenshotDOMElement({
      path:
        !process.env.ACCESS_KEY ||
        !process.env.SECRET_KEY ||
        !process.env.ENDPOINT
          ? process.env.IMAGE_PATH
            ? `${process.env.IMAGE_PATH}/${random_id}.jpg`
            : `./src/${random_id}.jpg`
          : undefined,
      selector: (selector as string) || "#topic-modelling-line-graph",
      padding: 16,
      page: page,
    });
    browser.close();
    if (
      process.env.ACCESS_KEY &&
      process.env.SECRET_KEY &&
      process.env.ENDPOINT
    )
      uploadImage({
        endpoint: process.env.ENDPOINT,
        imageBuffer: imageBuffer as Buffer,
        id: random_id,
      });
  }
);

interface uploadImageProps {
  endpoint: string;
  imageBuffer: Buffer;
  id: string;
}

const uploadImage = ({ endpoint, imageBuffer, id }: uploadImageProps) => {
  const spacesEndpoint = new AWS.Endpoint(endpoint);
  const s3 = new AWS.S3({
    endpoint: spacesEndpoint,
    accessKeyId: process.env.ACCESS_KEY,
    secretAccessKey: process.env.SECRET_KEY,
  });

  s3.putObject(
    {
      Body: imageBuffer,
      Bucket: "opendiscourse",
      Key: `${id}.jpg`,
      ACL: "public-read",
    },
    function (err, data) {
      if (err) console.log(err, err.stack);
      else console.log(data);
    }
  );
};

interface screenshotDOMElementProps {
  selector: string;
  padding: number;
  page: puppeteer.Page;
  path?: string;
}

const screenshotDOMElement = async ({
  selector,
  padding,
  page,
  path,
}: screenshotDOMElementProps) => {
  if (!selector) throw Error("Please provide a selector.");
  const rect = await page.evaluate((selector) => {
    const element = document.querySelector(selector);
    if (!element) return null;
    const { x, y, width, height } = element.getBoundingClientRect();
    return { left: x, top: y, width, height, id: element.id };
  }, selector);
  if (!rect)
    throw Error(`Could not find element that matches selector: ${selector}.`);
  return new Promise((resolve, _reject) => {
    setTimeout(() => {
      resolve(
        page.screenshot({
          path: path,
          type: "jpeg",
          quality: 100,
          clip: {
            x: rect.left - padding,
            y: rect.top - padding,
            width: rect.width + padding * 2,
            height: rect.height + padding * 2,
          },
        })
      );
    }, 2000);
  });
};

app.listen(5300, "0.0.0.0");
