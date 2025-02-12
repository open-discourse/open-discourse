import React from "react";
import { Text, TextProps } from "@chakra-ui/react";

export interface DefaultTextProps extends TextProps {}

export const DefaultText: React.FC<DefaultTextProps> = ({
  children,
  ...props
}) => {
  return (
    <Text
      fontSize={{
        base: "sm",
        sm: "xl",
        md: "2xl",
        lg: "2xl",
        xl: "4xl",
      }}
      marginBottom={{
        base: "4",
        md: "4",
        lg: "6",
        xl: "8",
      }}
      {...props}
    >
      {children}
    </Text>
  );
};
export default DefaultText;
