import {
  Flex,
  ThemeProvider,
  CSSReset,
  ColorModeProvider,
} from "@chakra-ui/core";
import { theme } from "@chakra-ui/core";
import { Header } from "./components/header";

export const BaseTemplate: React.FC = ({ children }) => {
  return (
    <ThemeProvider theme={theme}>
      <CSSReset />
      <ColorModeProvider>
        <Flex direction="column">
          <Header />
          <Flex padding="1.5rem" direction="column">
            {children}
          </Flex>
        </Flex>
      </ColorModeProvider>
    </ThemeProvider>
  );
};
