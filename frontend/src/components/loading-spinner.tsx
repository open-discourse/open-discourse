import React from "react";
import { Spinner, SpinnerProps } from "@chakra-ui/react";

export const LoadingSpinner = (props: SpinnerProps) => {
  return (
    <Spinner
      speed="0.66s"
      emptyColor="gray.200"
      color="blue.500"
      data-testid="loading-spinner"
      size="xl"
      thickness="4px"
      {...props}
    />
  );
};

export default LoadingSpinner;
