import React, { useState } from "react";
import { SearchResultRow } from "../hooks/use-manage-data";
import { ResultBox } from "./result-box";
import { SimpleGrid } from "@chakra-ui/react";
import {
  Stack,
  Flex,
  Text,
  useBreakpointValue,
  IconButton,
} from "@chakra-ui/react";
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from "react-feather";
import { convertPosition } from "../result-table/index";

interface ResultMobileProps {
  data: SearchResultRow[];
  pageSize?: number;
}

interface PageState {
  pageIndex: number;
  pageSize: number;
}

type TableIconButtonProps = {
  icon: any;
  onClick:
    | ((event: React.MouseEvent<HTMLElement, MouseEvent>) => void)
    | undefined;
  isDisabled: boolean;
  colorScheme?: string;
};
export const TableIconButton: React.FC<TableIconButtonProps> = ({
  icon,
  onClick,
  isDisabled,
  children,
  colorScheme,
  ...rest
}) => {
  return (
    <IconButton
      size="sm"
      icon={icon}
      borderWidth={1}
      onClick={onClick}
      colorScheme={colorScheme}
      isDisabled={isDisabled}
      aria-label="Table Icon button"
      {...rest}
    >
      {children}
    </IconButton>
  );
};

TableIconButton.defaultProps = {
  colorScheme: "gray",
};

export const ResultMobile = ({
  data,
  pageSize: initialPageSize,
}: ResultMobileProps) => {
  const [pageState, setPageState] = useState<PageState>({
    pageIndex: 0,
    pageSize: initialPageSize || 10,
  });
  const pageCount = Math.ceil(data.length / pageState.pageSize);
  const isDesktop = useBreakpointValue({
    base: false,
    lg: true,
  });
  return (
    <Stack>
      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={{ base: "4", md: "8" }}>
        {data
          .slice(
            pageState.pageIndex * pageState.pageSize,
            pageState.pageIndex * pageState.pageSize + pageState.pageSize
          )
          .map((row) => (
            <ResultBox
              data={{
                ...row,
                abbreviation:
                  row.abbreviation == "not found"
                    ? "Ohne Zurodnung"
                    : row.abbreviation,
                positionShort: convertPosition(row.positionShort),
              }}
              key={row.id}
            />
          ))}
      </SimpleGrid>
      <Flex
        paddingY="2rem"
        justifyContent="space-between"
        flexDirection="row"
        overflowX="hidden"
        overflowY="hidden"
      >
        <Flex flexDirection="row">
          <TableIconButton
            onClick={() => setPageState({ ...pageState, pageIndex: 0 })}
            isDisabled={pageState.pageIndex <= 0 || pageCount == 0}
            icon={<ChevronsLeft size={20} />}
          />
          <TableIconButton
            isDisabled={pageState.pageIndex <= 0 || pageCount == 0}
            onClick={() =>
              setPageState({
                ...pageState,
                pageIndex: pageState.pageIndex - 1,
              })
            }
            icon={<ChevronLeft size={20} />}
          />
        </Flex>
        <Flex justifyContent="center" alignItems="center">
          <Text mr={4}>
            Page{" "}
            <strong>
              {pageState.pageIndex + 1} of {pageCount}
            </strong>{" "}
          </Text>
          {isDesktop && (
            <select
              value={pageState.pageSize}
              onChange={(e) => {
                setPageState({
                  ...pageState,
                  pageSize: Number(e.target.value),
                });
              }}
            >
              {[5, 10, 20, 30, 40, 50].map((pageSize) => (
                <option key={pageSize} value={pageSize}>
                  Show {pageSize}
                </option>
              ))}
            </select>
          )}
        </Flex>
        <Flex flexDirection="row">
          <TableIconButton
            isDisabled={pageState.pageIndex >= pageCount - 1}
            onClick={() =>
              setPageState({ ...pageState, pageIndex: pageState.pageIndex + 1 })
            }
            icon={<ChevronRight size={20} />}
          />
          <TableIconButton
            onClick={() =>
              setPageState({
                ...pageState,
                pageIndex: pageCount ? pageCount - 1 : 1,
              })
            }
            isDisabled={pageState.pageIndex >= pageCount - 1}
            icon={<ChevronsRight size={20} />}
          />
        </Flex>
      </Flex>
    </Stack>
  );
};
