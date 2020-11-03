import { Flex, ChakraProvider } from "@chakra-ui/core";
import { theme } from "@chakra-ui/core";
import { Header } from "./components/header";

export const BaseTemplate: React.FC = ({ children }) => {
  return (
    <ChakraProvider resetCSS={true} theme={theme}>
      <Flex direction="column">
        <Header />
        <Flex padding="1.5rem" direction="column">
          {children}
        </Flex>
      </Flex>
    </ChakraProvider>
  );
};
