/* eslint-disable @typescript-eslint/no-explicit-any */
import React from "react";
import { IconButton } from "@chakra-ui/react";
type TableIconButtonProps = {
  icon: any;
  onClick:
    | ((event: React.MouseEvent<HTMLElement, MouseEvent>) => void)
    | undefined;
  isDisabled: boolean;
  colorScheme?: string;
};
export const TableIconButton: React.FC<TableIconButtonProps> = ({
  icon,
  onClick,
  isDisabled,
  children,
  colorScheme,
  ...rest
}) => {
  return (
    <IconButton
      size="sm"
      {...rest}
      icon={icon}
      borderWidth={1}
      onClick={onClick}
      colorScheme={colorScheme}
      isDisabled={isDisabled}
      aria-label="Table Icon button"
    >
      {children}
    </IconButton>
  );
};

TableIconButton.defaultProps = {
  colorScheme: "gray",
};
