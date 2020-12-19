import { SearchResultRow } from "../hooks/use-manage-data";
import {
  useBreakpointValue,
  Stack,
  Button,
  useDisclosure,
} from "@chakra-ui/react";
import React from "react";
import { DefaultText } from "@bit/limebit.limebit-ui.default-text";
import { SpeechModal } from "../speech-modal";

interface ResultBoxProps {
  data: SearchResultRow;
  pageSize?: number;
}

export const ResultBox = ({ data }: ResultBoxProps) => {
  const padding = useBreakpointValue({
    base: "2",
    sm: "2",
    md: "3",
    lg: "4",
    xl: "5",
  });
  const slicePoint = useBreakpointValue({ base: 40, sm: 80, md: 120 });
  const { isOpen, onOpen, onClose } = useDisclosure();
  const datestring = data.date && new Date(data.date).toLocaleDateString();
  return (
    <>
      <Stack
        maxWidth={{ base: "100%", md: "47vw" }}
        justifyContent="space-between"
        bg="gray.100"
        rounded="md"
        padding={padding}
        borderColor="gray.600"
        backgroundColor="gray.200"
        borderWidth="1px"
      >
        <DefaultText fontWeight="bold">
          {" "}
          {data.firstName + " " + data.lastName} ({data.abbreviation}) -{" "}
          {data.positionShort}
          {datestring ? <>, am {datestring}</> : null}:
        </DefaultText>
        <DefaultText noOfLines={{ base: 4, md: 6 }}>
          {data.speechContent}
        </DefaultText>

        <Button colorScheme="pink" onClick={onOpen}>
          Mehr
        </Button>
      </Stack>
      <SpeechModal data={data} isOpen={isOpen} onClose={onClose} />
    </>
  );
};
