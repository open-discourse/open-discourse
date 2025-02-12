/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/ban-types */
/* eslint-disable @typescript-eslint/ban-ts-comment */
// this component is based on https://codesandbox.io/s/chakra-ui-react-table-o6psn?file=/src/Table/index.tsx:0-5871
// following the discussion on https://github.com/chakra-ui/chakra-ui/issues/135

// @TODO: [AD-272] ts compile do not ignore ReactTable
// @ts-nocheck
import React from "react";
import {
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  ChevronUp,
} from "react-feather";
import { useMediaQuery } from "react-responsive";
import {
  Column,
  Row,
  usePagination,
  useSortBy,
  useTable,
  useGlobalFilter,
} from "react-table";

import { Table, Th, Td, Tr, Thead, Tbody } from "../table";
import { TableIconButton } from "./table-icon-button";
import { UpdateDataProps } from "./use-inline-edit";
import { EditableCell } from "./editable-cell";
import { Flex, Text } from "@chakra-ui/react";
import { GlobalFilter } from "./global-filter";

type ReactTableProps<D extends object = {}> = {
  data: any;
  columns: Column<D>[];
  pageSize?: number;
  tableHeading?: React.ReactNode;
  onRowClick?: (row: Row<D>) => void;
  selectedId?: string | undefined;
  enableSearch?: boolean;
  inLineEditConfig?: {
    updateData: ({ rowIndex, columnId, value }: UpdateDataProps) => void;
    skipPageReset: boolean;
  };
  searchBarColSpan?: number;
};

export const ReactTable = <D extends {}>({
  columns,
  data,
  tableHeading,
  pageSize: initialPageSize,
  onRowClick,
  selectedId,
  enableSearch,
  inLineEditConfig,
  searchBarColSpan,
}: ReactTableProps<D>) => {
  const tableColumns = React.useMemo(() => columns, [columns]);

  const isTabletOrMobile = useMediaQuery({ query: "(max-width: 40em)" });

  const {
    getTableProps,
    headerGroups,
    prepareRow,
    page,
    canPreviousPage,
    canNextPage,
    pageOptions,
    pageCount,
    gotoPage,
    nextPage,
    previousPage,
    setPageSize,

    preGlobalFilteredRows,
    setGlobalFilter,

    state: { pageIndex, pageSize, globalFilter },
  } = useTable<D>(
    {
      columns: tableColumns,
      data,
      initialState: { pageIndex: 0, pageSize: initialPageSize },
      autoResetPage: !inLineEditConfig?.skipPageReset,
      ...(inLineEditConfig && {
        updateData: inLineEditConfig.updateData,
        defaultColumn: { Cell: EditableCell },
      }),
    },
    useGlobalFilter,
    useSortBy,
    usePagination,
  );

  return (
    <Flex flexDirection="column" flex={1} maxWidth="100%" width="100%">
      {tableHeading && <Flex borderBottomWidth="1px">{tableHeading}</Flex>}
      <Table {...(getTableProps() as any)} data-testid="react-table">
        <Thead>
          {headerGroups.map((headerGroup, outerIndex) => (
            <Tr
              flex={1}
              flexDirection="row"
              {...headerGroup.getHeaderGroupProps()}
              key={outerIndex}
            >
              {headerGroup.headers.map((column, inderIndex) => (
                <Th
                  p={4}
                  bg="gray.100"
                  {...column.getHeaderProps()}
                  {...column.getSortByToggleProps()}
                  key={inderIndex}
                >
                  <Flex justifyContent="space-between">
                    <Text fontWeight="bold">{column.render("Header")}</Text>
                    {column.isSorted ? (
                      column.isSortedDesc ? (
                        <ChevronDown size={20} />
                      ) : (
                        <ChevronUp size={20} />
                      )
                    ) : (
                      ""
                    )}
                  </Flex>
                </Th>
              ))}
            </Tr>
          ))}
          {enableSearch && (
            <Tr>
              <Th
                {...{
                  colSpan: searchBarColSpan ? searchBarColSpan : columns.length,
                }}
                width="100%"
                style={{
                  textAlign: "left",
                }}
              >
                <GlobalFilter
                  preGlobalFilteredRows={preGlobalFilteredRows}
                  globalFilter={globalFilter}
                  setGlobalFilter={setGlobalFilter}
                />
              </Th>
            </Tr>
          )}
        </Thead>
        <Tbody flexDirection="column">
          {page.map(
            (row, outerIndex) =>
              prepareRow(row) || (
                <Tr
                  style={onRowClick && { cursor: "pointer" }}
                  bg={row.id === selectedId ? "gray.100" : undefined}
                  onClick={() => onRowClick && onRowClick(row)}
                  flexDirection="row"
                  {...row.getRowProps()}
                  data-testid="table-row"
                  key={outerIndex}
                >
                  {row.cells.map((cell, innerIndex) => {
                    return (
                      <Td
                        justifyContent="flex-start"
                        p={4}
                        {...cell.getCellProps()}
                        data-testid="react-table-cell"
                        key={innerIndex}
                      >
                        {cell.render("Cell")}
                      </Td>
                    );
                  })}
                </Tr>
              ),
          )}
        </Tbody>
      </Table>
      <Flex
        paddingY="2rem"
        justifyContent="space-between"
        flexDirection="row"
        borderTopWidth="1px"
        overflowX="hidden"
        overflowY="hidden"
      >
        <Flex flexDirection="row">
          <TableIconButton
            onClick={() => gotoPage(0)}
            isDisabled={!canPreviousPage}
            icon={<ChevronsLeft size={20} />}
          />
          <TableIconButton
            isDisabled={!canPreviousPage}
            onClick={() => previousPage()}
            icon={<ChevronLeft size={20} />}
          />
        </Flex>
        <Flex justifyContent="center" alignItems="center">
          <Text mr={4}>
            Page{" "}
            <strong>
              {pageIndex + 1} of {pageOptions.length}
            </strong>{" "}
          </Text>
          {!isTabletOrMobile && (
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
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
            isDisabled={!canNextPage}
            onClick={() => nextPage()}
            icon={<ChevronRight size={20} />}
          />
          <TableIconButton
            onClick={() => gotoPage(pageCount ? pageCount - 1 : 1)}
            isDisabled={!canNextPage}
            icon={<ChevronsRight size={20} />}
          />
        </Flex>
      </Flex>
    </Flex>
  );
};
