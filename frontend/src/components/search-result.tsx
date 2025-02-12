import React from "react";
import { useManageData } from "./hooks/use-manage-data";
import { ResultTable } from "./result-table";
import { ResultMobile } from "./result-mobile";
import { useBreakpointValue } from "@chakra-ui/react";
import LoadingSpinner from "./loading-spinner";
import { ErrorToast } from "./error-toast";

export const SearchResult = (): React.ReactElement | null => {
  const { data, loading, error } = useManageData();
  const isDesktop = useBreakpointValue({
    md: false,
    lg: true,
  });

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorToast error={{ message: error.message, name: "Error" }} />;
  }

  return data ? (
    isDesktop ? (
      <ResultTable data={data} />
    ) : (
      <ResultMobile data={data} />
    )
  ) : null;
};
