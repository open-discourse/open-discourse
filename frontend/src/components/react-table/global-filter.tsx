/* eslint-disable @typescript-eslint/no-explicit-any */
import React from "react";
import { Row } from "react-table";
import { Input, InputGroup, InputLeftElement } from "@chakra-ui/react";
import { SearchIcon } from "@chakra-ui/icons";

interface GlobalFilterProps {
  preGlobalFilteredRows: Row<any>[];
  globalFilter: any;
  setGlobalFilter: (value: any) => void;
}
export const GlobalFilter: React.FC<GlobalFilterProps> = ({
  preGlobalFilteredRows,
  globalFilter,
  setGlobalFilter,
}) => {
  const count = preGlobalFilteredRows.length;

  return (
    <InputGroup>
      <InputLeftElement>
        <SearchIcon color="gray.300" />
      </InputLeftElement>
      <Input
        type="phone"
        placeholder={`Search ${count} records...`}
        value={globalFilter}
        onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
          setGlobalFilter(event.target.value);
        }}
      />
    </InputGroup>
  );
};
