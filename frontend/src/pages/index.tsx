import { BaseTemplate } from "../templates/base-template";
import { Flex } from "@chakra-ui/react";
import { SearchForm } from "../components/search-form";
import { SearchResult } from "../components/search-result";
import { DefaultContainer } from "@bit/limebit.limebit-ui.default-container";
import React from "react";

export interface QueryParams {
  first?: number;
  contentQuery?: string;
  nameQuery?: string;
  positionQuery?: string;
  fromDate?: string;
  toDate?: string;
}

const Search: React.FC = () => {
  return (
    <BaseTemplate>
      <Flex direction="column">
        <DefaultContainer size="l">
          <SearchForm />
          <SearchResult />
        </DefaultContainer>
      </Flex>
    </BaseTemplate>
  );
};

export default Search;
