import React from "react";
import { Flex, Heading } from "@chakra-ui/react";

export const Header: React.FC = () => {
  return (
    <Flex
      as="nav"
      align="center"
      justify="space-between"
      wrap="wrap"
      padding="1.5rem"
      bg="pink.500"
      color="white"
      width="100%"
    >
      <Heading as="h1" size="lg" letterSpacing={"-.1rem"}>
        Open Discourse Volltextsuche
      </Heading>
    </Flex>
  );
};
