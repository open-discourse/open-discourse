import { LoadingSpinner } from "@bit/limebit.chakra-ui-recipes.loading-spinner";
import { ErrorToast } from "@bit/limebit.chakra-ui-recipes.error-toast";
import React from "react";
import { useManageData } from "./hooks/use-manage-data";
import { ResultTable } from "./result-table";

export const SearchResult = (): React.ReactElement | null => {
  const { data, loading, error } = useManageData();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorToast error={{ message: error.message, name: "Error" }} />;
  }

  return data ? <ResultTable data={data} /> : null;
};

export default SearchResult;
