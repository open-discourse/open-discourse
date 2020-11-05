import { BaseTemplate } from "../templates/base-template";
import { Heading, Flex, Stack } from "@chakra-ui/core";
import { SearchForm } from "../components/search-form";
import { SearchResult } from "../components/search-result";
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
        <Heading>Full Text Search</Heading>
        <Stack>
          <SearchForm />
          <SearchResult />
        </Stack>
      </Flex>
    </BaseTemplate>
  );
};

export default Search;
