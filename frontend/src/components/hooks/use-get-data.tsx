import { useEffect, useState } from "react";

export const useGetData = <T,>(
  path: string,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  responseCallback: (response: any) => T,
): [T | undefined, () => void] => {
  const [data, setData] = useState<T>();
  const fetchQuery = () => {
    (async () => {
      const baseUrl =
        process.env.NEXT_PUBLIC_PROXY_ENDPOINT ||
        (await fetch("/proxy-host").then((r) => r.text()));

      console.log("baseUrl", baseUrl);

      const searchResult = await fetch(baseUrl + "/" + path, {
        mode: "cors",
      }).then((response) => response.json());
      const dataResult = responseCallback(searchResult.data);
      if (dataResult) {
        setData(dataResult);
      }
    })();
  };
  useEffect(() => fetchQuery(), []);
  return [data, fetchQuery];
};
