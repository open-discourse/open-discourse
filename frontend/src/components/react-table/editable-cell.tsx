/* eslint-disable @typescript-eslint/no-explicit-any */
import { Text, Input, ButtonGroup, IconButton } from "@chakra-ui/react";
import { CheckIcon, CloseIcon } from "@chakra-ui/icons";
import React from "react";
import { UpdateDataProps } from "./use-inline-edit";

export interface EditableCellProps {
  value: any;
  row: { index: any };
  column: { id: any };
  updateData: ({ rowIndex, columnId, value }: UpdateDataProps) => void;
}

export interface EditableControlsProps {
  isEditing: boolean;
}

export const EditableCell = ({
  value: initialValue,
  row,
  column: { id },
  updateData,
}: EditableCellProps) => {
  const [isEditing, setIsEditing] = React.useState(false);
  const [value, setValue] = React.useState(initialValue);

  const onSubmit = (newValue: string) => {
    updateData({ value: newValue, rowIndex: row.index, columnId: id });
  };

  return isEditing ? (
    <>
      <Input
        value={value}
        size="sm"
        onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
          setValue(event.target.value)
        }
      />
      {
        <ButtonGroup justifyContent="center" size="xs">
          <IconButton
            icon={<CheckIcon />}
            onClick={() => {
              onSubmit(value);
              setIsEditing(false);
            }}
            aria-label="Save"
          />
          <IconButton
            icon={<CloseIcon />}
            onClick={() => {
              setValue(initialValue);
              setIsEditing(false);
            }}
            aria-label="Cancel"
          />
        </ButtonGroup>
      }
    </>
  ) : (
    <Text onClick={() => setIsEditing(true)}>{initialValue}</Text>
  );
};
