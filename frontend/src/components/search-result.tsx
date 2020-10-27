import {
  Link,
  Text,
  Button,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  useDisclosure,
} from "@chakra-ui/core";
import { ReactTable } from "@bit/limebit.chakra-ui-recipes.react-table";
import { ExternalLinkIcon } from "@chakra-ui/icons";
import { useRouter } from "next/router";
import React, { useEffect, useState } from "react";

interface SearchResultRow {
  date: string;
  firstName: string;
  lastName: string;
  documentUrl: string;
  positionShort: string;
  speechContent: string;
  abbreviation: string;
}

interface Row {
  values: SearchResultRow;
}

const columns = [
  {
    Header: "ID",
    accessor: "id",
  },
  { Header: "First Name", accessor: "firstName" },
  { Header: "Last Name", accessor: "lastName" },
  { Header: "Faction", accessor: "abbreviation" },
  { Header: "Position", accessor: "positionShort" },
  {
    Header: "Date",
    accessor: "date",
    Cell: ({ row }: { row: Row }) => {
      if (row.values.date) {
        return <Text>{new Date(row.values.date).toLocaleDateString()}</Text>;
      }
      return null;
    },
  },
  {
    Header: "Url",
    accessor: "documentUrl",
    Cell: ({ row }: { row: Row }) => {
      if (row.values.documentUrl) {
        return (
          <Link href={row.values.documentUrl} isExternal>
            Protokoll <ExternalLinkIcon mx="2px" />
          </Link>
        );
      }
      return null;
    },
  },
  {
    Header: "Rede",
    accessor: "speechContent",
    Cell: ({ row }: { row: Row }) => {
      const { isOpen, onOpen, onClose } = useDisclosure();
      if (row.values.speechContent) {
        return (
          <>
            <Text>
              <Link onClick={onOpen}>{"anzeigen"}</Link>
            </Text>

            <Modal isOpen={isOpen} onClose={onClose} size={"xl"}>
              <ModalOverlay>
                <ModalContent>
                  <ModalHeader>Redebeitrag</ModalHeader>
                  <ModalCloseButton />

                  <ModalBody>
                    <Text mb="0.8rem">
                      {row.values.documentUrl && (
                        <Link href={row.values.documentUrl} isExternal>
                          Zum Plenarprotokoll <ExternalLinkIcon mx="2px" />
                        </Link>
                      )}
                    </Text>
                    <Text fontWeight="bold" mb="0.5rem">
                      {row.values.firstName} {row.values.lastName} (
                      {row.values.abbreviation}),{" "}
                      {row.values.date &&
                        new Date(row.values.date).toLocaleDateString()}
                      :
                    </Text>
                    <Text>{row.values.speechContent}</Text>
                  </ModalBody>

                  <ModalFooter>
                    <Button colorScheme="blue" mr={3} onClick={onClose}>
                      Schließen
                    </Button>
                  </ModalFooter>
                </ModalContent>
              </ModalOverlay>
            </Modal>
          </>
        );
      }
    },
  },
];

export const SearchResult = (): React.ReactElement => {
  const [data, setData] = useState<SearchResultRow[]>([]);
  const router = useRouter();
  useEffect(() => {
    const callApiAsync = async () => {
      const searchApiEndpoint = `http://167.99.244.228/${window.location.search}`;

      const searchResult = await fetch(searchApiEndpoint, {
        mode: "cors",
        headers: { "Content-Type": "application/json" },
      }).then((response) => response.json());
      if (searchResult.data.searchSpeeches) {
        setData(searchResult.data.searchSpeeches);
      }
    };

    callApiAsync();
  }, [router.query]);
  return (
    <ReactTable columns={columns} data={data} enableSearch pageSize={10} />
  );
};

export default SearchResult;
