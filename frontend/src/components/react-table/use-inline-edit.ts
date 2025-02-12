/* eslint-disable @typescript-eslint/no-explicit-any */
import React from "react";
import { MutationFunctionOptions } from "@apollo/react-common";

export interface UpdateDataProps {
  rowIndex: number;
  columnId: string;
  value: string | number;
}

export interface UseInLineEditProps {
  tableData: object[];
  dbUpdateCallback?: (
    options?: MutationFunctionOptions<any, any>,
  ) => Promise<any>;
}

export interface UseInLineEditReturnType {
  data: object;
  setData: React.Dispatch<React.SetStateAction<object[]>>;
  inLineEditConfig: {
    updateData: ({ rowIndex, columnId, value }: UpdateDataProps) => void;
    skipPageReset: boolean;
    setSkipPageReset: React.Dispatch<React.SetStateAction<boolean>>;
  };
}

export const useInlineEdit = (
  props: UseInLineEditProps,
): UseInLineEditReturnType => {
  const [data, setData] = React.useState(props.tableData);
  const [skipPageReset, setSkipPageReset] = React.useState(false);
  React.useEffect(() => {
    setSkipPageReset(false);
  }, [data]);
  const updateData = ({ rowIndex, columnId, value }: UpdateDataProps) => {
    setSkipPageReset(true);
    setData((old) =>
      old.map((row, index) => {
        if (index === rowIndex) {
          if (props.dbUpdateCallback) {
            props.dbUpdateCallback({
              variables: { ...row, [columnId]: value },
            });
          }
          return {
            ...old[rowIndex],
            [columnId]: value,
          };
        }
        return row;
      }),
    );
  };
  return {
    data: data,
    setData: setData,
    inLineEditConfig: {
      updateData: updateData,
      skipPageReset: skipPageReset,
      setSkipPageReset: setSkipPageReset,
    },
  };
};
