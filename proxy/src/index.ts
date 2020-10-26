import express = require("express");
const fetch = require("node-fetch");

const app = express();

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
  const variables = `"variables":{"first":50,"contentQuery":"${
    contentQuery || ""
  }${
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
  const result = await fetch(process.env.GRAPHQL_ENDPOINT, {
    method: "POST",
    mode: "cors",
    headers: { "Content-Type": "application/json" },
    body: query,
  });
  const searchResult = await result.json();
  res.send(searchResult);
});

app.listen(80, "0.0.0.0");
