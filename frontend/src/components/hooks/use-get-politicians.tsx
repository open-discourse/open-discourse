import { useEffect, useState } from "react";

export interface Politician {
  id: number;
  firstName: string;
  lastName: string;
}

export const useGetPoliticians = (): [Politician[], () => void] => {
  const [politicians, setPoliticians] = useState<Politician[]>([]);
  const fetchQuery = () => {
    (async () => {
      const searchResult = await fetch("http://167.99.244.228/politicians", {
        mode: "cors",
      }).then((response) => response.json());
      const politiciansResult = searchResult.data.politicians;
      if (politiciansResult) {
        setPoliticians(politiciansResult);
      }
    })();
  };
  useEffect(() => fetchQuery(), []);
  return [politicians, fetchQuery];
};

export default useGetPoliticians;
