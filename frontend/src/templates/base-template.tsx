import { Flex, ChakraProvider, extendTheme } from "@chakra-ui/react";
import { createBreakpoints } from "@chakra-ui/theme-tools";
import { Header } from "./components/header";

const breakpoints = createBreakpoints({
  sm: "480px",
  md: "768px",
  lg: "1024px",
  xl: "2560px",
});

const extendedTheme = {
  breakpoints,
  colors: {
    pink: {
      500: "#EB558A",
    },
    gray: {
      100: "#F2F2F2",
      200: "#E9E9E9",
      300: "#CCCCCC",
    },
  },
  styles: { global: { body: { bg: "gray.50" } } },
};
const customTheme = extendTheme(extendedTheme);

export const BaseTemplate: React.FC = ({ children }) => {
  return (
    <ChakraProvider resetCSS={true} theme={customTheme}>
      <Flex direction="column">
        <Header />
        <Flex padding="1.5rem" direction="column">
          {children}
        </Flex>
      </Flex>
    </ChakraProvider>
  );
};
