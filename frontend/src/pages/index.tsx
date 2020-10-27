import { BaseTemplate } from "../templates/base-template";
import { Heading, Flex } from "@chakra-ui/core";
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

        <Flex flex={1} p={4}>
          <SearchForm />
        </Flex>
        <SearchResult />
      </Flex>
    </BaseTemplate>
  );
};

export default Search;
