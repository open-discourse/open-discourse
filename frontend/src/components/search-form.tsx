import queryString from "query-string";
import { Stack, Input, Button } from "@chakra-ui/core";
import { useState, useEffect, FormEvent } from "react";
import { useRouter } from "next/router";
import { useGetPoliticians } from "../components/hooks/use-get-politicians";
import { useGetFactions } from "../components/hooks/use-get-factions";
import AsyncSelect from "react-select/async";
import Select from "react-select";

export interface FormParams {
  contentQuery?: string | null;
  factionIdQuery?: number | null;
  politicianIdQuery?: number | null;
  positionShortQuery?: string | null;
  fromDate?: string | null;
  toDate?: string | null;
}

export interface Faction {
  id: number;
  fullName: string;
  abbreviation: string;
}

export const SearchForm: React.FC<FormParams> = () => {
  const [formParams, setFormParams] = useState<FormParams>({});
  const [politicians] = useGetPoliticians();
  const [factions] = useGetFactions();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    // do not refresh entire page
    event.preventDefault();
    // remove empty values from search string
    const searchValues: { [key: string]: any } = { ...formParams };
    Object.keys(searchValues).forEach(
      (key) =>
        searchValues[key] === (undefined || "") && delete searchValues[key]
    );
    router.push(
      `/?${queryString.stringify(JSON.parse(JSON.stringify(searchValues)))}`
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
      factionIdQuery: (factionIdQuery as unknown) as number,
      politicianIdQuery: (politicianIdQuery as unknown) as number,
      positionShortQuery: positionShortQuery as string,
      fromDate: fromDate as string,
      toDate: toDate as string,
    });
  }, [router.query]);

  const convertedPoliticians = politicians
    ? politicians.map((politician) => ({
        value: politician.id,
        label: `${politician.firstName} ${politician.lastName}`,
      }))
    : [];

  const convertedFactions = factions
    ? factions.map((faction) => ({
        value: faction.id,
        label: faction.fullName,
      }))
    : [];

  const filterPoliticians = (inputValue: string) => {
    return convertedPoliticians.filter((politician) =>
      politician.label.toLowerCase().includes(inputValue.toLowerCase())
    );
  };

  // Timeout for performance. jeez...
  const loadOptionsPoliticians = (inputValue: string, callback: any) => {
    setTimeout(() => {
      callback(filterPoliticians(inputValue));
    }, 1000);
  };

  const positions = [
    { value: "Member of Parliament", label: "Member of Parliament" },
    { value: "Presidium of Parliament", label: "Presidium of Parliament" },
    { value: "Guest", label: "Guest" },
    { value: "Chancellor", label: "Chancellor" },
    { value: "Minister", label: "Minister" },
    { value: "Secretary of State", label: "Secretary of State" },
    { value: "Not found", label: "Not found" },
  ];

  if (politicians && factions) {
    return (
      <>
        <form onSubmit={handleSubmit}>
          <Stack spacing={3}>
            <AsyncSelect
              cacheOptions
              defaultOptions
              loadOptions={loadOptionsPoliticians}
              onChange={(event) => {
                setFormParams({
                  ...formParams,
                  // event type is not correct
                  politicianIdQuery: (event as any)["value"] as number,
                });
              }}
              {...(formParams.politicianIdQuery
                ? {
                    value: convertedPoliticians.find(
                      (politician) =>
                        politician.value == formParams.politicianIdQuery
                    ),
                  }
                : {})}
            />
            <Select
              options={convertedFactions}
              onChange={(event) => {
                setFormParams({
                  ...formParams,
                  // event type is not correct
                  factionIdQuery: (event as any)["value"] as number,
                });
              }}
              {...(formParams.factionIdQuery
                ? {
                    value: convertedFactions.find(
                      (faction) => faction.value == formParams.factionIdQuery
                    ),
                  }
                : {})}
            />
            <Select
              options={positions}
              onChange={(event) => {
                setFormParams({
                  ...formParams,
                  // event type is not correct
                  positionShortQuery: (event as any)["value"] as string,
                });
              }}
              {...(formParams.positionShortQuery
                ? {
                    value: positions.find(
                      (position) =>
                        position.value == formParams.positionShortQuery
                    ),
                  }
                : {})}
            />
            <Input
              value={formParams?.contentQuery || ""}
              placeholder="Redebeitrag"
              onChange={(event: React.ChangeEvent<HTMLInputElement>): void =>
                setFormParams({
                  ...formParams,
                  contentQuery: event.target.value,
                })
              }
            />
            <Stack isInline>
              <Input
                value={formParams?.fromDate || ""}
                placeholder="Von"
                type="date"
                onChange={(event: React.ChangeEvent<HTMLInputElement>): void =>
                  setFormParams({
                    ...formParams,
                    fromDate: event.target.value,
                  })
                }
              />
              <Input
                value={formParams?.toDate || ""}
                placeholder="Bis"
                type="date"
                onChange={(event: React.ChangeEvent<HTMLInputElement>): void =>
                  setFormParams({
                    ...formParams,
                    toDate: event.target.value,
                  })
                }
              />
            </Stack>
          </Stack>
          <Button mt={3} colorScheme="teal" type="submit">
            Suchen
          </Button>
        </form>
      </>
    );
  }
  return null;
};
