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
  Checkbox,
  Flex,
} from "@chakra-ui/core";
import { ReactTable } from "@bit/limebit.chakra-ui-recipes.react-table";
import { ExternalLinkIcon } from "@chakra-ui/icons";
import React, { useReducer } from "react";
import { SearchResultRow } from "./hooks/use-manage-data";
import { DownloadButton } from "./download-button";

interface ResultTableProps {
  data: SearchResultRow[];
}

interface Row {
  values: SearchResultRow;
}

type SelectedState = { [id: number]: boolean };
type SelectedAction = {
  action: "toggleSingle";
  id: number;
};

const convertPosition = (position: string) => {
  switch (position) {
    case "Member of Parliament":
      return "Mitglied des Bundestages";
    case "Presidium of Parliament":
      return "Mitglied des Präsidiums";
    case "Guest":
      return "Gast";
    case "Chancellor":
      return "Kanzerl_in";
    case "Minister":
      return "Minister_in";
    case "Secretary of State":
      return "Staatssekretär_in";
    default:
      return "Nicht gefunden";
  }
};

export const ResultTable = ({ data }: ResultTableProps) => {
  const [selected, dispatchSelected] = useReducer(
    (currentState: SelectedState, action: SelectedAction): SelectedState => {
      switch (action.action) {
        case "toggleSingle":
          return {
            ...currentState,
            [action.id]: !currentState[action.id],
          };
      }
    },
    Object.fromEntries(data.map((element) => [element.downloadId, false]))
  );

  const columns = [
    {
      Header: "Herunterladen",
      accessor: "downloadId",
      Cell: ({ row }: { row: Row }) => {
        if (row.values.downloadId) {
          return (
            <Checkbox
              isChecked={selected[row.values.downloadId]}
              onChange={() => {
                dispatchSelected({
                  action: "toggleSingle",
                  id: row.values.downloadId,
                });
              }}
            />
          );
        }
        return null;
      },
    },
    {
      Header: "ID",
      accessor: "id",
    },
    { Header: "Vorname", accessor: "firstName" },
    { Header: "Nachname", accessor: "lastName" },
    { Header: "Fraktion", accessor: "abbreviation" },
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

              <Modal isOpen={isOpen} onClose={onClose} size={"6xl"}>
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
                      <Text whiteSpace="pre-line">
                        {row.values.speechContent}
                      </Text>
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
  return (
    <>
      <ReactTable
        columns={columns}
        data={data.map((element) => {
          return {
            ...element,
            positionShort: convertPosition(element.positionShort),
          };
        })}
        pageSize={10}
      />
      <Flex>
        <DownloadButton data={data} text={"Alles Herunterladen"} />
        {Object.entries(selected).some(([_id, state]) => state) ? (
          <DownloadButton
            data={data.filter((element) => selected[element.downloadId])}
            text={"Ausgewählte Herunterladen"}
          />
        ) : null}
      </Flex>
    </>
  );
};
