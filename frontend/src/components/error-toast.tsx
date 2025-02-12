import { useToast } from "@chakra-ui/react";
import { useEffect } from "react";
import React from "react";

interface ErrorToastProps {
  error: Error;
}

const Toast: React.FC<ErrorToastProps> = ({ error }) => {
  const toast = useToast();

  useEffect(() => {
    if (error) {
      toast({
        title: "An error occurred.",
        description: error.message,
        status: "error",
        duration: 9000,
        isClosable: true,
      });
    }
  }, [error, toast]);
  return null;
};

export const ErrorToast: React.FC<ErrorToastProps> = ({ error }) => {
  return <Toast error={error} />;
};
