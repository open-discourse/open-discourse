import {
  Input,
  InputGroup,
  InputLeftAddon,
  InputRightElement,
} from "@chakra-ui/react";
import React from "react";
import { CalendarIcon } from "@chakra-ui/icons";
import { ChangeEvent } from "react";
import SelectInput, { DataProps } from "./select-input";

export interface FormParams {
  contentQuery?: string | null;
  factionIdQuery?: string | null;
  politicianIdQuery?: string | null;
  positionShortQuery?: string | null;
  fromDate?: string | null;
  toDate?: string | null;
}

export interface DefaultDateInputProps {
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
  value: string;
  prefix: string;
}

export const DefaultDateInput = ({
  onChange,
  value,
  prefix,
}: DefaultDateInputProps) => {
  return (
    <InputGroup>
      <InputLeftAddon>{prefix}</InputLeftAddon>
      <Input
        value={value}
        placeholder="YYYY-MM-DD"
        type="date"
        focusBorderColor="pink.500"
        onChange={onChange}
      />
      <InputRightElement>{<CalendarIcon color="pink.500" />}</InputRightElement>
    </InputGroup>
  );
};

export interface DefaultSelectInputProps {
  rawData: DataProps[];
  onSelect: (element: DataProps | undefined) => void;
  placeholder: string;
  initialValue?: DataProps;
}

export const DefaultSelectInput = ({
  rawData,
  onSelect,
  placeholder,
  initialValue,
}: DefaultSelectInputProps) => {
  return (
    <SelectInput
      width="100%"
      placeholder={placeholder}
      rawData={rawData}
      onSelect={onSelect}
      InputProps={{
        focusBorderColor: "pink.500",
        type: "text",
      }}
      BoxProps={{
        backgroundColor: "white",
        borderWidth: "1px",
        borderColor: "gray.200",
      }}
      ButtonProps={{
        textColor: "black",
        rounded: "0px",
        _hover: { backgroundColor: "gray.200" },
        paddingX: "1",
      }}
      iconColor="pink.500"
      iconHoverColor="pink.100"
      initialValue={initialValue}
    />
  );
};
