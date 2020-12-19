import { useEffect, useState } from "react";
import { useRouter } from "next/router";

export interface SearchResultRow {
  id: number;
  downloadId: number;
  date: string;
  firstName: string;
  lastName: string;
  documentUrl: string;
  positionShort: string;
  speechContent: string;
  abbreviation: string;
}

interface Error {
  message: string;
}

export const useManageData = () => {
  const [data, setData] = useState<SearchResultRow[]>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error>();
  const router = useRouter();
  useEffect(() => {
    const callApiAsync = async () => {
      setData(undefined);
      setLoading(true);
      setError(undefined);
      const searchApiEndpoint = `${
        process.env.PROXY_ENDPOINT || "https://api.opendiscourse.de:5300"
      }/${window.location.search}`;

      const searchResult = await fetch(searchApiEndpoint, {
        mode: "cors",
        headers: { "Content-Type": "application/json" },
      }).then((response) => response.json());
      if (searchResult.errors) {
        setError(searchResult.errors[0]);
      }
      if (searchResult.data.searchSpeeches) {
        setData(
          searchResult.data.searchSpeeches.map((user: { id: number }) => ({
            ...user,
            downloadId: user.id,
          }))
        );
      }
      setLoading(false);
    };

    callApiAsync();
  }, [router.query]);

  return { data, loading, error };
};
