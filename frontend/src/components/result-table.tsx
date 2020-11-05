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
import React, { useState } from "react";
import { SearchResultRow } from "./hooks/use-manage-data";

interface ResultTableProps {
  data: SearchResultRow[];
}

interface Row {
  values: SearchResultRow;
}

export const ResultTable = ({ data }: ResultTableProps) => {
  const [selected, setSelected] = useState(
    data.map((element) => {
      return { id: element.downloadId, state: false };
    })
  );

  const columns = [
    {
      Header: "Download",
      accessor: "downloadId",
      Cell: ({ row }: { row: Row }) => {
        if (row.values.downloadId) {
          return (
            <Checkbox
              isChecked={
                selected.find((element) => element.id == row.values.downloadId)
                  ?.state
              }
              onChange={(e) => {
                const newselected = selected.filter(
                  (element) => element.id != row.values.downloadId
                );
                newselected.push({
                  id: row.values.downloadId,
                  state: e.target.checked,
                });
                setSelected(newselected);
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
      <ReactTable columns={columns} data={data} pageSize={10} />
      <Flex>
        <a
          download={"test.csv"}
          href={`data:text/csv;base64,${btoa(
            unescape(
              encodeURIComponent(
                "id,firstname,lastname,faction,position,date, url,speech\n" +
                  data
                    .map(
                      (element) =>
                        `${JSON.stringify(element.id)},${JSON.stringify(
                          JSON.stringify(element.firstName)
                        )},${JSON.stringify(element.lastName)},${JSON.stringify(
                          element.abbreviation
                        )},${JSON.stringify(
                          element.positionShort
                        )},${JSON.stringify(element.date)},${JSON.stringify(
                          element.documentUrl
                        )},${JSON.stringify(element.speechContent)}\n`
                    )
                    .reduce((a, b) => a + b, "")
              )
            )
          )}`}
        >
          <Button colorScheme="teal">Download All</Button>
        </a>
        {selected.filter((element) => element.state == true).length > 0 ? (
          <a
            style={{ marginLeft: "10px" }}
            download={"test.csv"}
            href={`data:text/csv;base64,${btoa(
              unescape(
                encodeURIComponent(
                  "id,firstname,lastname,faction,position,date, url,speech\n" +
                    data
                      .filter(
                        (element) =>
                          selected.find(
                            (selectedElement) =>
                              selectedElement.id == element.downloadId
                          )?.state == true
                      )
                      .map(
                        (element) =>
                          `${JSON.stringify(element.id)},${JSON.stringify(
                            JSON.stringify(element.firstName)
                          )},${JSON.stringify(
                            element.lastName
                          )},${JSON.stringify(
                            element.abbreviation
                          )},${JSON.stringify(
                            element.positionShort
                          )},${JSON.stringify(element.date)},${JSON.stringify(
                            element.documentUrl
                          )},${JSON.stringify(element.speechContent)}\n`
                      )
                      .reduce((a, b) => a + b, "")
                )
              )
            )}`}
          >
            <Button colorScheme="teal">Download Selected</Button>
          </a>
        ) : null}
      </Flex>
    </>
  );
};
