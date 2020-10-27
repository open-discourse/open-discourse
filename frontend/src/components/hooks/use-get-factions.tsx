import { useEffect, useState } from "react";

export interface Faction {
  id: number;
  fullName: string;
  abbreviation: string;
}

export const useGetFactions = (): [Faction[], () => void] => {
  const [factions, setPoliticians] = useState<Faction[]>([]);
  const fetchQuery = () => {
    (async () => {
      const searchResult = await fetch("http://167.99.244.228/factions", {
        mode: "cors",
      }).then((response) => response.json());
      const factionsResult = searchResult.data.factions;
      if (factionsResult) {
        setPoliticians(factionsResult);
      }
    })();
  };
  useEffect(() => fetchQuery(), []);
  return [factions, fetchQuery];
};

export default useGetFactions;
