import queryString from "query-string";
import { Stack, Input } from "@chakra-ui/react";
import { useState, useEffect, FormEvent } from "react";
import { useRouter } from "next/router";
import { useGetData } from "./hooks/use-get-data";
import {
  DefaultDateInput,
  FormParams,
  DefaultSelectInput,
} from "./custom-inputs";
import React from "react";
import DefaultButton from "./default-components/default-button";

export interface Faction {
  id: string;
  fullName: string;
  abbreviation: string;
}

export interface Politician {
  id: string;
  firstName: string;
  lastName: string;
}

export const positions = [
  { key: "Member of Parliament", label: "Mitglied des Bundestages" },
  { key: "Presidium of Parliament", label: "Mitglied des Präsidiums" },
  { key: "Guest", label: "Gast" },
  { key: "Chancellor", label: "Kanzler_in" },
  { key: "Minister", label: "Minister_in" },
  { key: "Secretary of State", label: "Staatssekretär_in" },
  { key: "Not found", label: "Unbekannt" },
];

export const SearchForm: React.FC<FormParams> = () => {
  const [formParams, setFormParams] = useState<FormParams>({});
  const [politicians] = useGetData<Politician[]>(
    `politicians`,
    (response) => response.politicians,
  );
  const [factions] = useGetData<Faction[]>(
    `factions`,
    (response) => response.factions,
  );

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    // do not refresh entire page
    event.preventDefault();
    // remove empty values from search string
    const searchValues: { [key: string]: unknown } = { ...formParams };
    Object.keys(searchValues).forEach((key) => {
      if (searchValues[key] === undefined || searchValues[key] === "") {
        delete searchValues[key];
      }
    });
    router.push(
      `/?${queryString.stringify(JSON.parse(JSON.stringify(searchValues)))}`,
    );
  };

  const router = useRouter();
  useEffect(() => {
    const {
      contentQuery,
      factionIdQuery,
      politicianIdQuery,
      positionShortQuery,
      fromDate,
      toDate,
    } = router.query;
    setFormParams({
      contentQuery: contentQuery as string,
      factionIdQuery: factionIdQuery as string,
      politicianIdQuery: politicianIdQuery as string,
      positionShortQuery: positionShortQuery as string,
      fromDate: fromDate as string,
      toDate: toDate as string,
    });
  }, [router.query]);

  const convertedPoliticians = politicians
    ? politicians.map((politician) => ({
        key: politician.id,
        label: `${politician.firstName} ${politician.lastName}`,
      }))
    : [];

  const convertedFactions = factions
    ? factions
        .filter(
          (faction) => !["1", "8", "9", "10", "12", "19"].includes(faction.id),
        )
        .map((faction) => ({
          key: faction.id,
          label: faction.id == "-1" ? "Ohne Zuordnung" : faction.fullName,
        }))
    : [];

  if (politicians && factions) {
    return (
      <>
        <form onSubmit={handleSubmit}>
          <Stack spacing={{ base: 2, md: 3 }}>
            <Input
              value={formParams?.contentQuery || ""}
              placeholder="Redeinhalt Durchsuchen"
              focusBorderColor="pink.500"
              onChange={(event: React.ChangeEvent<HTMLInputElement>): void =>
                setFormParams({
                  ...formParams,
                  contentQuery: event.target.value,
                })
              }
              type="text"
            />
            <Stack direction={{ base: "column", md: "row" }}>
              <DefaultSelectInput
                rawData={convertedPoliticians}
                onSelect={(element) => {
                  setFormParams({
                    ...formParams,
                    politicianIdQuery: element?.key,
                  });
                }}
                initialValue={
                  formParams.politicianIdQuery
                    ? convertedPoliticians.find(
                        (politician) =>
                          politician.key == formParams.politicianIdQuery,
                      )
                    : undefined
                }
                placeholder="Nach Politiker_Innen Filtern"
              />
              <DefaultSelectInput
                rawData={convertedFactions}
                onSelect={(element) => {
                  setFormParams({
                    ...formParams,
                    factionIdQuery: element?.key,
                  });
                }}
                initialValue={
                  formParams.factionIdQuery
                    ? convertedFactions.find(
                        (faction) => faction.key == formParams.factionIdQuery,
                      )
                    : undefined
                }
                placeholder="Nach Fraktion Filtern"
              />
              <DefaultSelectInput
                rawData={positions}
                onSelect={(element) => {
                  setFormParams({
                    ...formParams,
                    positionShortQuery: element?.key,
                  });
                }}
                initialValue={
                  formParams.positionShortQuery
                    ? positions.find(
                        (position) =>
                          position.key == formParams.positionShortQuery,
                      )
                    : undefined
                }
                placeholder="Nach Position Filtern"
              />
            </Stack>
            <Stack direction={{ base: "column", md: "row" }}>
              <DefaultDateInput
                prefix="Von:"
                onChange={(event) => {
                  setFormParams({
                    ...formParams,
                    fromDate: event.target.value,
                  });
                }}
                value={formParams?.fromDate || ""}
              />
              <DefaultDateInput
                prefix="Bis:"
                onChange={(event) => {
                  setFormParams({
                    ...formParams,
                    toDate: event.target.value,
                  });
                }}
                value={formParams?.toDate || ""}
              />
            </Stack>
          </Stack>
          <DefaultButton
            rightIcon={undefined}
            mt={3}
            colorScheme="pink"
            type="submit"
            marginY="30px"
          >
            Suchen
          </DefaultButton>
        </form>
      </>
    );
  }
  return null;
};
