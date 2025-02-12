import { SearchResultRow } from "./hooks/use-manage-data";
import {
  Text,
  Button,
  Modal,
  ModalOverlay,
  ModalHeader,
  ModalContent,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
} from "@chakra-ui/react";
import { ArrowForwardIcon } from "@chakra-ui/icons";
import React from "react";
import DefaultText from "./default-components/default-text";
import NextChakraLink from "./next-chakra-link";

export interface SpeechModalProps {
  isOpen: boolean;
  onClose: () => void;
  data: SearchResultRow;
}

export const SpeechModal = ({ isOpen, onClose, data }: SpeechModalProps) => {
  const datestring = data.date && new Date(data.date).toLocaleDateString();
  return (
    <Modal isOpen={isOpen} onClose={onClose} size={"4xl"}>
      <ModalOverlay>
        <ModalContent>
          <ModalHeader>
            <DefaultText fontWeight="bold">Redebeitrag</DefaultText>
          </ModalHeader>
          <ModalCloseButton
            bg="pink.500"
            color="white"
            _hover={{ bg: "pink.600" }}
          />

          <ModalBody>
            <Text mb="5" color="pink.500" fontWeight="bold">
              {data.documentUrl && (
                <>
                  <NextChakraLink
                    color="pink.500"
                    href={data.documentUrl}
                    isExternal
                  >
                    <ArrowForwardIcon mr="1" />
                    Zum Plenarprotokoll
                  </NextChakraLink>
                </>
              )}
            </Text>
            <Text fontWeight="bold">
              {data.firstName} {data.lastName} ({data.abbreviation})
            </Text>
            <Text fontWeight="bold" mb="1">
              {data.positionShort}
            </Text>
            <Text fontWeight="bold" mb="1">
              {datestring}
            </Text>
            <Text whiteSpace="pre-line">{data.speechContent}</Text>
          </ModalBody>

          <ModalFooter>
            <Button colorScheme="pink" mr={3} onClick={onClose}>
              Schließen
            </Button>
          </ModalFooter>
        </ModalContent>
      </ModalOverlay>
    </Modal>
  );
};
