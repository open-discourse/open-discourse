import React from "react";
import { BoxProps, Box } from "@chakra-ui/react";

export const Table: React.FC<BoxProps> = ({ children, ...rest }) => {
  return (
    <Box
      table-layout="auto"
      border-collapse="collapse"
      style={{ tableLayout: "fixed", width: "100%" }}
      {...{ as: "table" }}
      {...rest}
    >
      {children}
    </Box>
  );
};
export const Thead: React.FC<BoxProps> = ({ children, ...rest }) => {
  return (
    <Box p={4} textAlign="left" {...{ as: "thead" }} {...rest}>
      {children}
    </Box>
  );
};

export const Tbody: React.FC<BoxProps> = ({ children, ...rest }) => {
  return (
    <Box p={4} {...{ as: "tbody" }} {...rest}>
      {children}
    </Box>
  );
};

export const Tfoot: React.FC<BoxProps> = ({ children, ...rest }) => {
  return (
    <Box p={4} {...{ as: "tfoot" }} {...rest}>
      {children}
    </Box>
  );
};

export const Th: React.FC<BoxProps> = ({ children, ...rest }) => {
  return (
    <Box
      padding={4}
      borderBottom="1px"
      borderBottomColor="gray.200"
      {...{ as: "th" }}
      {...rest}
    >
      {children}
    </Box>
  );
};

export const Tr: React.FC<BoxProps> = ({ children, ...rest }) => {
  return (
    <Box my={1} {...{ as: "tr" }} {...rest}>
      {children}
    </Box>
  );
};

export const Td: React.FC<BoxProps> = ({ children, ...rest }) => (
  <Box
    p={4}
    borderBottom="1px"
    borderBottomColor="gray.200"
    {...{ as: "td" }}
    {...rest}
  >
    {children}
  </Box>
);
