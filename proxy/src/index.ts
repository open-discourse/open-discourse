import express = require("express");
import mcache from "memory-cache";
import fetch from "node-fetch";
import cors from "cors";

const app = express();

app.use(cors());

const cache = (duration: number) => {
  return (
    req: express.Request,
    res: express.Response,
    next: express.NextFunction
  ) => {
    const key = "__express__" + req.originalUrl || req.url;
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

app.get("/", async function (req, res) {
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
  const variables = `"variables":{"first":${
    process.env.QUERY_LIMIT || "50"
  },"contentQuery":"${contentQuery || ""}${
    factionIdQuery
      ? `","factionIdQuery":"${(factionIdQuery as unknown) as number}`
      : ""
  }${
    politicianIdQuery
      ? `","politicianIdQuery":"${(politicianIdQuery as unknown) as number}`
      : ""
  }","positionShortQuery":"${positionShortQuery || ""}"${
    fromDate ? `,"fromDate":"${fromDate}"` : ""
  }${toDate ? `,"toDate":"${toDate}"` : ""}}`;
  const query = `{"operationName":"Search",${variables},"query":"query Search($contentQuery: String, $factionIdQuery: BigInt, $politicianIdQuery: BigInt, $positionShortQuery: String, $fromDate: Date, $toDate: Date, $first: Int!) {\\n searchSpeeches(first: $first, politicianIdQuery: $politicianIdQuery, positionShortQuery: $positionShortQuery, factionIdQuery: $factionIdQuery, fromDate: $fromDate, toDate: $toDate, contentQuery: $contentQuery) {\\n rank\\n id\\n firstName\\n lastName\\n positionShort\\n date\\n  documentUrl\\n speechContent\\n abbreviation\\n}\\n}\\n"}`;
  const result = await fetch(process.env.GRAPHQL_ENDPOINT as string, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: query,
  });
  const searchResult = await result.json();
  res.send(searchResult);
});

app.get(
  "/politicians",
  cache(((process.env.CACHE_EXPIRATION as unknown) as number) || 1),
  async (_req, res) => {
    const query = `{"operationName":"Politicians","query":"query Politicians {\\n politicians {\\n id\\n firstName\\n lastName\\n} \\n}"}`;
    const result = await fetch(process.env.GRAPHQL_ENDPOINT as string, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: query,
    });
    const searchResult = await result.json();
    res.send(searchResult);
  }
);

app.get(
  "/factions",
  cache(((process.env.CACHE_EXPIRATION as unknown) as number) || 1),
  async (_req, res) => {
    const query = `{"operationName":"Factions","query":"query Factions {\\n factions {\\n id\\n fullName\\n abbreviation\\n }\\n \\n}"}`;
    const result = await fetch(process.env.GRAPHQL_ENDPOINT as string, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: query,
    });
    const searchResult = await result.json();
    res.send(searchResult);
  }
);

app.listen(80, "0.0.0.0");
