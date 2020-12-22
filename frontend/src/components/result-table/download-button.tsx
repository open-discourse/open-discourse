import { SearchResultRow } from "../hooks/use-manage-data";
import { DownloadIcon } from "@chakra-ui/icons";
import { DefaultButton } from "@bit/limebit.limebit-ui.default-button";

export interface DownloadButtonProps {
  data: SearchResultRow[];
  text: string;
}

export const DownloadButton = ({ data, text }: DownloadButtonProps) => (
  <a
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
    <DefaultButton rightIcon={<DownloadIcon />} colorScheme="pink">
      {text}
    </DefaultButton>
  </a>
);
