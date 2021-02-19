import express = require("express");
import puppeteer from "puppeteer";
import mcache from "memory-cache";
import fetch from "node-fetch";
import { v4 } from "uuid";
import AWS from "aws-sdk";
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
    if ((req.originalUrl || req.url).startsWith("/?")) {
      fetch(
        (process.env.GRAPHQL_ENDPOINT ||
          "http://localhost:5000/graphql") as string,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: `{
          "operationName":"FtsTracking",
          "variables":{"searchQuery":"${req.originalUrl || req.url}"},
          "query":"mutation FtsTracking($searchQuery:String!) {createFtsTracking(input: {ftsTracking: {searchQuery: $searchQuery}}) {clientMutationId}}"
        }`,
        }
      );
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
    const result = await fetch(
      (process.env.GRAPHQL_ENDPOINT ||
        "http://localhost:5000/graphql") as string,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: query,
      }
    );
    const searchResult = await result.json();
    res.send(searchResult);
  }
);

app.get(
  "/politicians",
  cache(((process.env.CACHE_EXPIRATION as unknown) as number) || 1),
  async (_req, res) => {
    const query = `{"operationName":"Politicians","query":"query Politicians {\\n politicians {\\n id\\n firstName\\n lastName\\n} \\n}"}`;
    const result = await fetch(
      (process.env.GRAPHQL_ENDPOINT ||
        "http://localhost:5000/graphql") as string,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: query,
      }
    );
    const searchResult = await result.json();
    res.send(searchResult);
  }
);

app.get(
  "/factions",
  cache(((process.env.CACHE_EXPIRATION as unknown) as number) || 1),
  async (_req, res) => {
    const query = `{"operationName":"Factions","query":"query Factions {\\n factions {\\n id\\n fullName\\n abbreviation\\n }\\n \\n}"}`;
    const result = await fetch(
      (process.env.GRAPHQL_ENDPOINT ||
        "http://localhost:5000/graphql") as string,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: query,
      }
    );
    const searchResult = await result.json();
    res.send(searchResult);
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
