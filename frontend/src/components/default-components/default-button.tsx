import React from "react";
import { Button, ButtonProps } from "@chakra-ui/react";
import { ArrowForwardIcon } from "@chakra-ui/icons";

export interface DefaultButtonProps extends ButtonProps {
  colorScheme: string;
}
export const DefaultButton: React.FC<DefaultButtonProps> = ({
  children,
  colorScheme,
  ...props
}) => {
  return (
    <Button
      colorScheme={colorScheme}
      size={"md"}
      fontSize={{ xl: "2xl" }}
      padding={{ xl: "8" }}
      textTransform="uppercase"
      rightIcon={<ArrowForwardIcon />}
      {...props}
    >
      {children}
    </Button>
  );
};
export default DefaultButton;
