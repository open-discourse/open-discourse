import React from "react";
import { Container, ContainerProps } from "@chakra-ui/react";

export interface DefaultContainerProps extends ContainerProps {
  size: "s" | "m" | "l" | "xl";
}
export const containerSizes = {
  s: { base: "100vw", sm: "400px", md: "500px", lg: "850px", xl: "60vw" },
  m: { base: "100vw", sm: "500px", md: "600px", lg: "1050px", xl: "65vw" },
  l: { base: "100vw", sm: "500px", md: "900px", lg: "1250px", xl: "70vw" },
  xl: { base: "100vw", sm: "500px", md: "900px", lg: "1400px", xl: "80vw" },
};
export const DefaultContainer: React.FC<DefaultContainerProps> = ({
  size,
  children,
  ...props
}) => {
  return (
    <Container
      maxW={containerSizes[size]}
      {...props}
      marginLeft="auto"
      marginRight="auto"
    >
      {children}
    </Container>
  );
};
export default DefaultContainer;
