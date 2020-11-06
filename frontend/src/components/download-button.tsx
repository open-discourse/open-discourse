import { SearchResultRow } from "./hooks/use-manage-data";
import { Button } from "@chakra-ui/core";

export interface DownloadButtonProps {
  data: SearchResultRow[];
  text: string;
}

export const DownloadButton = ({ data, text }: DownloadButtonProps) => (
  <a
    style={{ margin: "5px" }}
    download={"OpenDiscourseData.csv"}
    href={`data:text/csv;base64,${btoa(
      unescape(
        encodeURIComponent(
          "id,firstname,lastname,faction,position,date, url,speech\n" +
            data
              .map(
                (element) =>
                  `${JSON.stringify(element.id)},${JSON.stringify(
                    element.firstName
                  )},${JSON.stringify(element.lastName)},${JSON.stringify(
                    element.abbreviation
                  )},${JSON.stringify(element.positionShort)},${JSON.stringify(
                    element.date
                  )},${JSON.stringify(element.documentUrl)},${JSON.stringify(
                    element.speechContent
                  )}\n`
              )
              .reduce((a, b) => a + b, "")
        )
      )
    )}`}
  >
    <Button colorScheme="teal">{text}</Button>
  </a>
);
