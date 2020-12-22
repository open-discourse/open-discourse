import { useEffect, useState } from "react";

export const useGetData = <T,>(
  queryUrl: string,
  responseCallback: (response: any) => T
): [T | undefined, () => void] => {
  const [data, setData] = useState<T>();
  const fetchQuery = () => {
    (async () => {
      const searchResult = await fetch(queryUrl, {
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
