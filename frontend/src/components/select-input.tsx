import React, { useState } from "react";
import {
  Input,
  Box,
  Button,
  Text,
  InputGroup,
  InputRightElement,
  ResponsiveValue,
  BoxProps,
  InputProps,
  ButtonProps,
  TextProps,
} from "@chakra-ui/react";
import { SearchIcon, CloseIcon } from "@chakra-ui/icons";
import * as CSS from "csstype";

export interface DataProps {
  label: string;
  key: string;
}

export interface SelectInputProps {
  placeholder: string;
  rawData: DataProps[];
  width?: string;
  first?: number;
  onSelect?: (element: DataProps | undefined) => void;
  BoxProps?: BoxProps;
  InputProps?: InputProps;
  ButtonProps?: ButtonProps;
  TextProps?: TextProps;
  iconColor?: ResponsiveValue<CSS.Property.BackgroundImage>;
  iconHoverColor?: ResponsiveValue<CSS.Property.BackgroundImage>;
  boxHoverColor?: ResponsiveValue<CSS.Property.BackgroundImage>;
  initialValue?: DataProps;
}

export const SelectInput = ({
  width,
  placeholder,
  rawData,
  onSelect,
  BoxProps,
  ButtonProps,
  InputProps,
  TextProps,
  iconColor,
  iconHoverColor,
  boxHoverColor,
  initialValue,
  first = 50,
}: SelectInputProps): JSX.Element => {
  const [focusedInput, setFocusedInput] = useState(false);
  const [focusedButton, setFocusedButton] = useState(false);
  const [selected, setSelected] = useState<DataProps | null>(
    initialValue || null,
  );
  const [input, setInput] = useState(initialValue?.label);

  return (
    <Box position="relative" display="inline-block" width={width}>
      <InputGroup
        onFocus={() => setFocusedInput(true)}
        onBlur={() => {
          setTimeout(() => {
            if (!selected) setInput("");
            setFocusedInput(false);
          }, 150);
        }}
      >
        <Input
          {...InputProps}
          placeholder={placeholder}
          onChange={(e) => {
            setInput(e.target.value);
            setSelected(null);
          }}
          value={selected ? selected.label : input}
          width="100%"
        />
        <InputRightElement>
          {selected ? (
            <CloseIcon
              boxSize="25px"
              color={iconColor}
              borderRadius="0.5em"
              padding="4px"
              cursor="pointer"
              _hover={{ backgroundColor: iconHoverColor }}
              onClick={() => {
                setInput("");
                setSelected(null);
                if (onSelect) onSelect(undefined);
              }}
            />
          ) : (
            <SearchIcon color={iconColor} />
          )}
        </InputRightElement>
      </InputGroup>
      {focusedInput || focusedButton ? (
        <Box
          {...BoxProps}
          position="absolute"
          width="100%"
          maxHeight="200px"
          overflowY="auto"
          marginTop="6px"
          shadow="sm"
          rounded="4px"
          zIndex="20"
          onFocus={() => setFocusedButton(true)}
          onBlur={() => setFocusedButton(false)}
          _focus={{ outline: "None" }}
        >
          {rawData
            .filter(
              (element) =>
                input &&
                element.label.toLowerCase().includes(input?.toLowerCase()),
            )
            .slice(0, first)
            .map((element) => (
              <Button
                _hover={{ backgroundColor: boxHoverColor }}
                {...ButtonProps}
                variant="ghost"
                width="100%"
                textAlign="left"
                onClick={() => {
                  setInput(element.label);
                  setSelected(element);
                  setFocusedButton(false);
                  setFocusedInput(false);
                  if (onSelect) onSelect(element);
                }}
                key={element.key}
              >
                <Text
                  fontWeight="normal"
                  {...TextProps}
                  paddingLeft="10px"
                  width="100%"
                >
                  {element.label}
                </Text>
              </Button>
            ))}
        </Box>
      ) : null}
    </Box>
  );
};

export default SelectInput;
